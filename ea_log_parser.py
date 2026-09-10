import re
import os
import time
from datetime import datetime
from threading import Thread

class EALogParser:
    """解析MT5 EA日志文件，实时获取EA内部数据"""
    
    def __init__(self, log_dir=None):
        self.log_dir = log_dir or r"D:\MetaTrader 5 EXNESS\MQL5\Logs"
        self.current_price = 0.0
        self.high_100 = 0.0
        self.low_100 = 0.0
        self.dist_ma = 0.0
        self.slope_m1 = 0.0
        self.slope_m6 = 0.0
        self.atr_ok = False
        self.freq_ok = False
        self.session = ""
        self.version = ""
        self.last_log_size = 0
        self._stop = False
        self._thread = None
        self.callbacks = []
        
    def start(self):
        """启动后台解析线程"""
        self._stop = False
        self._thread = Thread(target=self._parse_loop, daemon=True)
        self._thread.start()
        
    def stop(self):
        """停止解析"""
        self._stop = True
        
    def add_callback(self, callback):
        """添加数据更新回调"""
        self.callbacks.append(callback)
        
    def _parse_loop(self):
        """后台解析循环"""
        while not self._stop:
            try:
                self._parse_latest_log()
            except Exception as e:
                pass
            time.sleep(0.5)  # 每0.5秒检查一次
            
    def _parse_latest_log(self):
        """解析最新的日志文件"""
        try:
            # 找到最新的日志文件
            log_files = [f for f in os.listdir(self.log_dir) if f.endswith('.log')]
            if not log_files:
                return
                
            latest_log = max(log_files)
            log_path = os.path.join(self.log_dir, latest_log)
            
            # 检查文件大小变化
            file_size = os.path.getsize(log_path)
            if file_size == self.last_log_size:
                return
            self.last_log_size = file_size
            
            # 读取最后100行
            with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()[-100:]
                
            for line in lines:
                self._parse_line(line)
                
        except Exception as e:
            pass
            
    def _parse_line(self, line):
        """解析单行日志"""
        try:
            # 解析最高价格
            if "最高价格—————" in line:
                match = re.search(r'最高价格—————([0-9.]+)', line)
                if match:
                    self.high_100 = float(match.group(1))
                    
            # 解析最低价格
            if "最低价格—————" in line:
                match = re.search(r'最低价格—————([0-9.]+)', line)
                if match:
                    self.low_100 = float(match.group(1))
                    
            # 解析距离均线
            if "距离M1均线" in line and ":" in line:
                match = re.search(r'距离M1均线.+: ([0-9.]+)', line)
                if match:
                    self.dist_ma = float(match.group(1))
                    
            # 解析次线倾斜
            if "次线M1倾斜" in line and ":" in line:
                match = re.search(r'次线M1倾斜.+: ([0-9.]+)', line)
                if match:
                    self.slope_m1 = float(match.group(1))
                    
            # 解析主线倾斜
            if "主线M6倾斜" in line and ":" in line:
                match = re.search(r'主线M6倾斜.+: ([0-9.]+)', line)
                if match:
                    self.slope_m6 = float(match.group(1))
                    
            # 解析ATR许可
            if "ATRINT许可" in line:
                self.atr_ok = "通过" in line
                
            # 解析频率许可
            if "主线M1频率" in line:
                self.freq_ok = "通过" in line
                
            # 解析时段
            if "当前为" in line and "时段" in line:
                match = re.search(r'当前为([^=]+)时段', line)
                if match:
                    self.session = match.group(1).strip()
                    
            # 解析版本号
            if "版本号" in line and "V" in line:
                match = re.search(r'V(\d+\.\d+)', line)
                if match:
                    self.version = match.group(1)
                    
            # 触发回调
            for cb in self.callbacks:
                cb(self.get_data())
                
        except Exception as e:
            pass
            
    def get_data(self):
        """获取当前解析数据"""
        return {
            'high_100': self.high_100,
            'low_100': self.low_100,
            'dist_ma': self.dist_ma,
            'slope_m1': self.slope_m1,
            'slope_m6': self.slope_m6,
            'atr_ok': self.atr_ok,
            'freq_ok': self.freq_ok,
            'session': self.session,
            'version': self.version,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        }
        
    def is_connected(self):
        """检查是否连接到EA"""
        return self.high_100 > 0 or self.low_100 > 0
