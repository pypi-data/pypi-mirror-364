import sys
import math
import time
from typing import Dict, Any, List, Union
import numpy as np
import socket
import threading
import time
import pickle
import queue
from . import util
import matplotlib.pyplot as plt

def _draw_bar(value: float, length: int = 30) -> str:
    """基本的なバーグラフを描画"""
    bar_len = min(length, max(0, int(value * length)))
    return '█' * bar_len + '-' * (length - bar_len)


def _draw_symmetric_bar(value: float, length: int = 30) -> str:
    """対称的なバーグラフを描画（-1.0から1.0の範囲）"""
    max_len = length // 2
    value = max(-1.0, min(1.0, value))
    if value >= 0:
        pos = int(value * max_len)
        return ' ' * max_len + '│' + '█' * pos + ' ' * (max_len - pos)
    else:
        neg = int(-value * max_len)
        return ' ' * (max_len - neg) + '█' * neg + '│' + ' ' * max_len


def _draw_balance_bar(value: float, length: int = 30) -> str:
    """0.5を中心としたバランスバーを描画"""
    max_len = length // 2
    value = max(0.0, min(1.0, value))
    diff = value - 0.5
    if diff > 0:
        right = int(diff * 2 * max_len + 0.5)
        return ' ' * max_len + '│' + '█' * right + ' ' * (max_len - right)
    else:
        left = int(-diff * 2 * max_len + 0.5)
        return ' ' * (max_len - left) + '█' * left + '│' + ' ' * max_len


def _rms(values: Union[List[float], tuple]) -> float:
    """RMS値を計算"""
    if not values:
        return 0.0
    return math.sqrt(sum(x * x for x in values) / len(values))


def _format_value(value: Any, max_length: int = 50) -> str:
    """値を適切な形式でフォーマット"""
    if isinstance(value, (list, tuple)):
        if len(value) > 0:
            if isinstance(value[0], (int, float)):
                # 数値のリストの場合、最初の数個の値を表示
                preview = value[:5]
                if len(value) > 5:
                    return f"[{', '.join(f'{v:.3f}' for v in preview)}...] ({len(value)} items)"
                else:
                    return f"[{', '.join(f'{v:.3f}' for v in preview)}]"
            else:
                return f"[{', '.join(str(v) for v in value[:3])}...]" if len(value) > 3 else str(value)
        else:
            return "[]"
    elif isinstance(value, float):
        return f"{value:.4f}"
    elif isinstance(value, int):
        return str(value)
    else:
        str_val = str(value)
        if len(str_val) > max_length:
            return str_val[:max_length-3] + "..."
        return str_val


def _get_bar_for_value(key: str, value: Any, bar_length: int = 30, bar_type: str = "normal") -> tuple[str, float]:
    """キーと値に基づいて適切なバーを選択"""
    if isinstance(value, (list, tuple)):
        if len(value) > 2:
            if isinstance(value[0], (int, float)):
                # 数値のリストの場合、RMS値を計算
                rms_val = _rms(value) * 3  # type: ignore
                return _draw_bar(rms_val, bar_length), rms_val
            else:
                return "N/A", 0.0
        elif len(value) == 2:
            value = value[1] / (value[0] + value[1])
            return _draw_balance_bar(float(value), bar_length), float(value)
        else:
            return "N/A", 0.0
    elif isinstance(value, (int, float)):
        return _draw_bar(float(value), bar_length), float(value)
    else:
        return "N/A", 0.0


class ConsoleBar:
    """
    maai.get_result()の内容をバーグラフで可視化するクラス
    """
    def __init__(self, bar_length: int = 30, bar_type: str = "normal"):
        self.bar_length = bar_length
        self.bar_type = bar_type
        self._first = True

    def update(self, result: Dict[str, Any]):
        if self._first:
            sys.stdout.write("\x1b[2J")  # 初期クリア
            self._first = False
        sys.stdout.write("\x1b[H")  # カーソルを左上に移動
        
        # 時刻の表示
        if 't' in result:
            dt = time.localtime(result['t'])
            ms = int((result['t'] - int(result['t'])) * 1000)
            print(f"Time: {dt.tm_year:04d}/{dt.tm_mon:02d}/{dt.tm_mday:02d} {dt.tm_hour:02d}:{dt.tm_min:02d}:{dt.tm_sec:02d}.{ms:03d}")
            print("-" * (self.bar_length + 30))
        
        # bar_typeがbalanceのとき、x1/x2の値とバーを2行で横並び表示
        if self.bar_type == "balance" and 'x1' in result and 'x2' in result:
            x1 = np.squeeze(np.array(result['x1'])).tolist()
            x2 = np.squeeze(np.array(result['x2'])).tolist()
            bar1, val1 = _get_bar_for_value('x1', x1, self.bar_length // 2 - 1, "normal")
            bar1 = bar1[::-1]
            bar2, val2 = _get_bar_for_value('x2', x2, self.bar_length // 2 - 1, "normal")
            print(f"x1 │ x2{' ' * 8}: {bar1} │ {bar2} ({val1:.4f}, {val2:.4f})")
        # 各キーを動的に処理
        for key, value in result.items():
            if key == 't':
                continue
            # x1/x2は既に横並びで表示したのでスキップ
            if self.bar_type == "balance" and key in ['x1', 'x2']:
                continue
            if not isinstance(value, (float, int)):
                value = np.squeeze(np.array(value)).tolist()
            bar, value = _get_bar_for_value(key, value, self.bar_length, self.bar_type)
            print(f"{key:15}: {bar} ({value:.3f})")
        print("-" * (self.bar_length + 30))

class TCPReceiver():
    def __init__(self, ip, port, mode):
        self.ip = ip
        self.port = port
        self.mode = mode
        self.sock = None
        self.result_queue = queue.Queue()
    
    def _bytearray_2_vapresult(self, data: bytes) -> Dict[str, Any]:
        if self.mode == 'vap':
            vap_result = util.conv_bytearray_2_vapresult(data)
        elif self.mode == 'bc-2type':
            vap_result = util.conv_bytearray_2_vapresult_bc_2type(data)
        elif self.mode == 'nod':
            vap_result = util.conv_bytearray_2_vapresult_nod(data)
        else:
            raise ValueError(f"Invalid mode: {self.mode}")
        return vap_result
    
    def connect_server(self):    
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.ip, self.port))
        print('[CLIENT] Connected to the server')

    def _start_client(self):
        while True:
            try:
                self.connect_server()
                while True:
                    try:
                        size = int.from_bytes(self.sock.recv(4), 'little')
                        data = b''
                        while len(data) < size:
                            data += self.sock.recv(size - len(data))
                        vap_result = self._bytearray_2_vapresult(data)
                        self.result_queue.put(vap_result)

                    except Exception as e:
                        print('[CLIENT] Receive error:', e)
                        break  # 受信エラー時は再接続ループへ
            except Exception as e:
                print('[CLIENT] Connect error:', e)
                time.sleep(0.5)
                continue
            # 切断時はソケットを閉じて再接続ループへ
            try:
                if hasattr(self, 'sock') and self.sock is not None:
                    self.sock.close()
            except Exception:
                pass
            self.sock = None
            print('[CLIENT] Disconnected. Reconnecting...')
            time.sleep(0.5)

    def start_process(self):
        threading.Thread(target=self._start_client, daemon=True).start()
    
    def get_result(self):
        return self.result_queue.get()

class TCPTransmitter:
    def __init__(self, ip, port, mode):
        self.ip = ip
        self.port = port
        self.mode = mode
        self.result_queue = queue.Queue()
    
    def _vapresult_2_bytearray(self, result_dict: Dict[str, Any]) -> bytes:
        if self.mode == 'vap':
            data_sent = util.conv_vapresult_2_bytearray(result_dict)
        elif self.mode == 'bc-2type':
            data_sent = util.conv_vapresult_2_bytearray_bc_2type(result_dict)
        elif self.mode == 'nod':
            data_sent = util.conv_vapresult_2_bytearray_nod(result_dict)
        else:
            raise ValueError(f"Invalid mode: {self.mode}")
        return data_sent
        
    def _start_server(self):
        while True:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.bind((self.ip, self.port))
                s.listen(1)
                print('[OUT] Waiting for connection...')
                conn, addr = s.accept()
                print('[OUT] Connected by', addr)
                while True:
                    try:
                        result_dict = self.result_queue.get()
                        data_sent = self._vapresult_2_bytearray(result_dict)
                        data_sent_all = len(data_sent).to_bytes(4, 'little') + data_sent
                        conn.sendall(data_sent_all)
                    except Exception as e:
                        print('[OUT] Send error:', e)
                        break
            except Exception as e:
                print('[OUT] Disconnected by', addr)
                print(e)
                continue
            
    def start_server(self):
        threading.Thread(target=self._start_server, daemon=True).start()
        
    def update(self, result: Dict[str, Any]):
        self.result_queue.put(result)

# 新規追加: GUIでバーグラフを表示するクラス
class GuiBar:
    """matplotlibを用いて結果をバーグラフでGUI表示するクラス"""
    def __init__(self, bar_type: str = "normal"):
        self.bar_type = bar_type
        self.plt = plt
        self.fig, self.ax = plt.subplots()
        plt.ion()
        plt.show()
        # バーアーティストを保持してリアルタイム更新
        self.bars = None

    def update(self, result: Dict[str, Any]):
        """resultのキーと値をバーグラフで更新表示する"""
        labels = []
        values = []
        for key, value in result.items():
            if key == 't':
                continue
            # 配列やリストは適切にスカラー化
            if not isinstance(value, (int, float)):
                value = np.squeeze(np.array(value)).tolist()
            if isinstance(value, (list, tuple)):
                if len(value) > 2 and isinstance(value[0], (int, float)):
                    val = _rms(value) * 3
                elif len(value) == 2:
                    total = value[0] + value[1]
                    val = (value[1] / total) if total != 0 else 0.0
                else:
                    val = 0.0
            else:
                try:
                    val = float(value)
                except Exception:
                    continue
            labels.append(key)
            values.append(val)
        # 初回描画またはラベル数が変わった場合は新規描画
        if self.bars is None or len(self.bars) != len(values):
            self.ax.clear()
            self.bars = self.ax.bar(labels, values, color='skyblue')
            self.ax.set_ylim(0, 1)
            self.ax.set_xticks(range(len(labels)))
            self.ax.set_xticklabels(labels)
            self.ax.set_title('Result Bar Graph')
        else:
            # 既存のバーを更新
            for bar, v in zip(self.bars, values):
                bar.set_height(v)
        # 描画を反映
        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()
        self.plt.pause(0.001)