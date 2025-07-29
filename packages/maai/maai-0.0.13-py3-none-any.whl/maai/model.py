import torch
import torch.nn as nn
import time
import numpy as np
import threading
import queue
import copy
import os

from .input import Base
from .util import load_vap_model
from .models.vap import VapGPT
from .models.vap_bc import VapGPT_bc
from .models.vap_nod import VapGPT_nod
from .models.config import VapConfig

class Maai():
    
    BINS_P_NOW = [0, 1]
    BINS_PFUTURE = [2, 3]
    
    CALC_PROCESS_TIME_INTERVAL = 100

    def __init__(self, mode, frame_rate, context_len_sec, language: str = "jp", audio_ch1: Base = None, audio_ch2: Base = None, num_channels: int = 2, cpc_model: str = os.path.expanduser("~/.cache/cpc/60k_epoch4-d0f474de.pt"), device: str = "cpu", cache_dir: str = None, force_download: bool = False):

        conf = VapConfig()
        if mode in ["vap", "vap_MC"]:
            self.vap = VapGPT(conf)
        elif mode == "bc":
            self.vap = VapGPT_bc(conf)
        elif mode == "nod":
            self.vap = VapGPT_nod(conf)

        self.device = device

        sd = load_vap_model(mode, frame_rate, context_len_sec, language, device, cache_dir, force_download)
        self.vap.load_encoder(cpc_model=cpc_model)
        self.vap.load_state_dict(sd, strict=False)

        # The downsampling parameters are not loaded by "load_state_dict"
        self.vap.encoder1.downsample[1].weight = nn.Parameter(sd['encoder.downsample.1.weight'])
        self.vap.encoder1.downsample[1].bias = nn.Parameter(sd['encoder.downsample.1.bias'])
        self.vap.encoder1.downsample[2].ln.weight = nn.Parameter(sd['encoder.downsample.2.ln.weight'])
        self.vap.encoder1.downsample[2].ln.bias = nn.Parameter(sd['encoder.downsample.2.ln.bias'])
        
        self.vap.encoder2.downsample[1].weight = nn.Parameter(sd['encoder.downsample.1.weight'])
        self.vap.encoder2.downsample[1].bias = nn.Parameter(sd['encoder.downsample.1.bias'])
        self.vap.encoder2.downsample[2].ln.weight = nn.Parameter(sd['encoder.downsample.2.ln.weight'])
        self.vap.encoder2.downsample[2].ln.bias = nn.Parameter(sd['encoder.downsample.2.ln.bias'])

        self.vap.to(self.device)
        self.vap = self.vap.eval()
        
        self.mode = mode
        self.mic1 = audio_ch1
        self.mic2 = audio_ch2

        # Always subscribe a dedicated queue for each mic if possible
        self._mic1_queue = self.mic1.subscribe()
        self._mic2_queue = self.mic2.subscribe()

        self.audio_contenxt_lim_sec = context_len_sec
        self.frame_rate = frame_rate
        
        # Context length of the audio embeddings (depends on frame rate)
        self.audio_context_len = int(self.audio_contenxt_lim_sec * self.frame_rate)
        
        self.sampling_rate = 16000
        self.frame_contxt_padding = 320 # Independe from frame size
        
        # Frame size
        # 10Hz -> 320 + 1600 samples
        # 20Hz -> 320 + 800 samples
        # 50Hz -> 320 + 320 samples
        self.audio_frame_size = self.sampling_rate // self.frame_rate + self.frame_contxt_padding
        
        self.current_x1_audio = []
        self.current_x2_audio = []
        
        self.result_p_now = 0.
        self.result_p_future = 0.
        self.result_p_bc_react = 0.
        self.result_p_bc_emo = 0.
        self.result_p_bc = 0.
        self.result_p_nod_short = 0.
        self.result_p_nod_long = 0.
        self.result_p_nod_long_p = 0.
        self.result_last_time = -1
        
        self.result_vad = [0., 0.]

        self.process_time_abs = -1

        self.e1_context = []
        self.e2_context = []
        
        self.list_process_time_context = []
        self.last_interval_time = time.time()
        
        self.result_dict_queue = queue.Queue()
    
    def worker(self):
        
        current_x1 = np.zeros(self.frame_contxt_padding)
        current_x2 = np.zeros(self.frame_contxt_padding)
        
        while True:
            
            # Always use get_audio_data(q) if queue is available
            x1 = self.mic1.get_audio_data(self._mic1_queue)
            x2 = self.mic2.get_audio_data(self._mic2_queue)
            
            current_x1 = np.concatenate([current_x1, x1])
            current_x2 = np.concatenate([current_x2, x2])

            # Continue to receive data until the size of the data is
            # less that the size of the VAP frame
            if len(current_x1) < self.audio_frame_size:
                continue
            
            self.process(current_x1, current_x2)
            
            # Save the last 320 samples
            current_x1 = current_x1[-self.frame_contxt_padding:]
            current_x2 = current_x2[-self.frame_contxt_padding:]
        
    def start_process(self):
        self.mic1.start_process()
        self.mic2.start_process()
        threading.Thread(target=self.worker, daemon=True).start()  
    
    def process(self, x1, x2):
        
        time_start = time.time()
        
        # Save the current audio data
        self.current_x1_audio = x1[self.frame_contxt_padding:]
        self.current_x2_audio = x2[self.frame_contxt_padding:]
        
        with torch.no_grad():
            
            # Convert to tensors efficiently
            x1_ = torch.from_numpy(x1).float().view(1, 1, -1).to(self.device)
            x2_ = torch.from_numpy(x2).float().view(1, 1, -1).to(self.device)

            e1, e2 = self.vap.encode_audio(x1_, x2_)
            
            self.e1_context.append(e1)
            self.e2_context.append(e2)
            
            if len(self.e1_context) > self.audio_context_len:
                self.e1_context = self.e1_context[-self.audio_context_len:]
            if len(self.e2_context) > self.audio_context_len:
                self.e2_context = self.e2_context[-self.audio_context_len:]
            
            x1_ = torch.cat(self.e1_context, dim=1).to(self.device)
            x2_ = torch.cat(self.e2_context, dim=1).to(self.device)

            o1 = self.vap.ar_channel(x1_, attention=False)  # ["x"]
            o2 = self.vap.ar_channel(x2_, attention=False)  # ["x"]
            out = self.vap.ar(o1["x"], o2["x"], attention=False)

            # Outputs
            if self.mode in ["vap", "vap_MC"]:
                logits = self.vap.vap_head(out["x"])
                
                vad1 = self.vap.va_classifier(o1["x"])
                vad2 = self.vap.va_classifier(o2["x"])
                
                probs = logits.softmax(dim=-1)
                
                p_now = self.vap.objective.probs_next_speaker_aggregate(
                    probs,
                    from_bin=self.BINS_P_NOW[0],
                    to_bin=self.BINS_P_NOW[-1]
                )
                
                p_future = self.vap.objective.probs_next_speaker_aggregate(
                    probs,
                    from_bin=self.BINS_PFUTURE[0],
                    to_bin=self.BINS_PFUTURE[1]
                )
                
                # Get back to the CPU
                p_now = p_now.to('cpu')
                p_future = p_future.to('cpu')
                
                vad1 = vad1.sigmoid().to('cpu')[::,-1]
                vad2 = vad2.sigmoid().to('cpu')[::,-1]
                
                self.result_p_now = p_now.tolist()[0][-1]
                self.result_p_future = p_future.tolist()[0][-1]
                
                self.result_vad = [vad1, vad2]
                
                self.result_dict_queue.put({
                    "t": time.time(),
                    "x1": copy.copy(self.current_x1_audio), "x2": copy.copy(self.current_x2_audio),
                    "p_now": copy.copy(self.result_p_now), "p_future": copy.copy(self.result_p_future),
                    "vad": copy.copy(self.result_vad)
                })
                
            elif self.mode == "bc":
                bc = self.vap.bc_head(out["x"])
                
                p_bc_react = bc.softmax(dim=-1)[:, -1, 1]
                p_bc_emo = bc.softmax(dim=-1)[:, -1, 2]
                
                # Get back to the CPU
                p_bc_react = p_bc_react.to('cpu')
                p_bc_emo = p_bc_emo.to('cpu')
                
                self.result_p_bc_react = [p_bc_react]#.tolist()[0][-1]
                self.result_p_bc_emo = [p_bc_emo]#.tolist()[0][-1]
                
                self.result_dict_queue.put({
                    "t": time.time(),
                    "x1": copy.copy(self.current_x1_audio), "x2": copy.copy(self.current_x2_audio),
                    "p_bc_react": copy.copy(self.result_p_bc_react), "p_bc_emo": copy.copy(self.result_p_bc_emo)
                })
            
            elif self.mode == "nod":
                
                p_bc = self.vap.bc_head(out["x"])
                nod = self.vap.nod_head(out["x"])
                
                p_bc = p_bc.sigmoid()[-1]
                p_nod_short = nod.softmax(dim=-1)[:, -1, 1]
                p_nod_long = nod.softmax(dim=-1)[:, -1, 2]
                p_nod_long_p = nod.softmax(dim=-1)[:, -1, 3]
                
                # Get back to the CPU
                p_bc = p_bc.to('cpu')
                p_nod_short = p_nod_short.to('cpu')
                p_nod_long = p_nod_long.to('cpu')
                p_nod_long_p = p_nod_long_p.to('cpu')
                
                self.result_p_bc = p_bc#.tolist()[0][-1]
                self.result_p_nod_short = [p_nod_short]#.tolist()[0][-1]
                self.result_p_nod_long = [p_nod_long]#.tolist()[0][-1]
                self.result_p_nod_long_p = [p_nod_long_p]#.tolist()[0][-1]
                
                self.result_dict_queue.put({
                    "t": time.time(),
                    "x1": copy.copy(self.current_x1_audio), "x2": copy.copy(self.current_x2_audio),
                    "p_bc": copy.copy(self.result_p_bc), "p_nod_short": copy.copy(self.result_p_nod_short), "p_nod_long": copy.copy(self.result_p_nod_long), "p_nod_long_p": copy.copy(self.result_p_nod_long_p)
                })
                
            # self.result_last_time = time.time()
            
            time_process = time.time() - time_start
            
            # Calculate the average encoding time
            self.list_process_time_context.append(time_process)
            
            if len(self.list_process_time_context) > self.CALC_PROCESS_TIME_INTERVAL:
                ave_proc_time = np.average(self.list_process_time_context)
                num_process_frame = len(self.list_process_time_context) / (time.time() - self.last_interval_time)
                self.last_interval_time = time.time()
                
                print('[VAP] Average processing time: %.5f [sec], #process/sec: %.3f' % (ave_proc_time, num_process_frame))
                self.list_process_time_context = []
            
            self.process_time_abs = time.time()
    
    def get_result(self):
        return self.result_dict_queue.get()
    