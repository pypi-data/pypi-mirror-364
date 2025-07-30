"""
Memory monitoring classes and utilities
"""

import threading
import time
import psutil
from dataclasses import dataclass, field

try:
    import pynvml
    NVML_AVAILABLE = True
except ImportError:
    NVML_AVAILABLE = False


@dataclass
class MemoryStats:
    """统计内存使用情况的数据类"""
    peak: float = 0.0
    min: float = field(default_factory=lambda: float('inf'))
    sum: float = 0.0
    count: int = 0

    @property
    def avg(self):
        """计算平均内存使用量"""
        return self.sum / self.count if self.count > 0 else 0.0


class SystemMonitor:
    """系统内存监控器"""
    
    def __init__(self, device_id=0, interval=0.1):
        """
        初始化系统监控器
        
        Args:
            device_id: GPU设备ID
            interval: 监控间隔（秒）
        """
        self.interval = interval
        self._stop_event = threading.Event()
        self.gpu_stats = MemoryStats()
        self.host_stats = MemoryStats()
        self.nvml_initialized = False
        self.handle = None
        self._thread = None
        
        # safely initialize pynvml
        if NVML_AVAILABLE:
            try:
                pynvml.nvmlInit()
                self.handle = pynvml.nvmlDeviceGetHandleByIndex(device_id)
                self.nvml_initialized = True
            except Exception as e:
                print(f"Warning: Failed to initialize GPU monitoring: {e}")
                self.nvml_initialized = False

    def _monitor_loop(self):
        """内存监控主循环"""
        while not self._stop_event.is_set():
            # collect GPU memory information
            if self.nvml_initialized:
                try:
                    gpu_info = pynvml.nvmlDeviceGetMemoryInfo(self.handle)
                    gpu_used = float(gpu_info.used) / 1024**3
                    
                    # update GPU statistics
                    self.gpu_stats.peak = max(self.gpu_stats.peak, gpu_used)
                    self.gpu_stats.min = min(self.gpu_stats.min, gpu_used)
                    self.gpu_stats.sum += gpu_used
                    self.gpu_stats.count += 1
                except Exception:
                    pass  # silently handle GPU errors during monitoring
            
            # collect host memory information
            try:
                host_info = psutil.virtual_memory()
                host_used = float(host_info.used) / 1024**3
                
                # update host statistics
                self.host_stats.peak = max(self.host_stats.peak, host_used)
                self.host_stats.min = min(self.host_stats.min, host_used)
                self.host_stats.sum += host_used
                self.host_stats.count += 1
            except Exception:
                pass  # silently handle host memory errors during monitoring
            
            time.sleep(self.interval)

    def start(self):
        """启动监控"""
        if self._thread is not None and self._thread.is_alive():
            return
            
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()

    def stop(self):
        """停止监控"""
        if self._thread is None:
            return
            
        self._stop_event.set()
        self._thread.join()
        
        # safely shutdown pynvml
        if self.nvml_initialized:
            try:
                pynvml.nvmlShutdown()
                self.nvml_initialized = False
            except Exception:
                pass

    def get_report(self):
        """获取监控报告"""
        gpu_min = self.gpu_stats.min if self.gpu_stats.min != float('inf') else 0.0
        host_min = self.host_stats.min if self.host_stats.min != float('inf') else 0.0
        
        return {
            "gpu_peak_gb": round(self.gpu_stats.peak, 2),
            "gpu_min_gb": round(gpu_min, 2),
            "gpu_avg_gb": round(self.gpu_stats.avg, 2),
            "host_peak_gb": round(self.host_stats.peak, 2),
            "host_min_gb": round(host_min, 2),
            "host_avg_gb": round(self.host_stats.avg, 2),
        } 