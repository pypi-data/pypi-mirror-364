"""
Memory scanner for executing commands and monitoring their memory usage
"""

import json
import subprocess
import time
from .monitor import SystemMonitor


class MemoryScanner:
    """内存扫描器，用于执行命令并监控其内存使用情况"""
    
    def __init__(self, args, command):
        """
        初始化扫描器
        
        Args:
            args: 命令行参数对象
            command: 要执行的命令列表
        """
        self.args = args
        self.command = command
        self.monitor = SystemMonitor(
            device_id=args.gpu_id,
            interval=args.interval
        )
        self.process = None
        
    def run_command(self):
        """执行目标命令并监控其内存使用情况"""
        print(f"Starting memory monitoring for: {' '.join(self.command)}")
        print(f"GPU ID: {self.args.gpu_id}, Interval: {self.args.interval}s")
        print("-" * 60)
        
        # start monitoring
        self.monitor.start()
        
        try:
            # execute the command
            start_time = time.time()
            self.process = subprocess.Popen(
                self.command,
                stdout=subprocess.PIPE if self.args.quiet else None,
                stderr=subprocess.PIPE if self.args.quiet else None,
                text=True
            )
            
            # wait for process to complete
            stdout, stderr = self.process.communicate()
            end_time = time.time()
            
            # stop monitoring
            self.monitor.stop()
            
            # print results
            self._print_results(start_time, end_time, stdout, stderr)
            
            return self.process.returncode
            
        except KeyboardInterrupt:
            print("\nInterrupted by user")
            if self.process:
                self.process.terminate()
            self.monitor.stop()
            return 1
        except Exception as e:
            print(f"Error executing command: {e}")
            self.monitor.stop()
            return 1
    
    def _print_results(self, start_time, end_time, stdout, stderr):
        """打印监控结果"""
        execution_time = end_time - start_time
        report = self.monitor.get_report()
        
        print("\n" + "=" * 60)
        print("MEMORY USAGE REPORT")
        print("=" * 60)
        
        print(f"Execution Time: {execution_time:.2f} seconds")
        print(f"Return Code: {self.process.returncode}")
        
        print("\nGPU Memory Usage:")
        print(f"  Peak: {report['gpu_peak_gb']} GB")
        print(f"  Min:  {report['gpu_min_gb']} GB")
        print(f"  Avg:  {report['gpu_avg_gb']} GB")
        
        print("\nHost Memory Usage:")
        print(f"  Peak: {report['host_peak_gb']} GB")
        print(f"  Min:  {report['host_min_gb']} GB")
        print(f"  Avg:  {report['host_avg_gb']} GB")
        
        if self.args.output:
            self._save_report(report, execution_time)
        
        if not self.args.quiet:
            if stdout:
                print("\nSTDOUT:")
                print(stdout)
            if stderr:
                print("\nSTDERR:")
                print(stderr)
    
    def _save_report(self, report, execution_time):
        """保存报告到文件"""
        full_report = {
            "execution_time": execution_time,
            "return_code": self.process.returncode,
            "memory_usage": report,
            "command": " ".join(self.command),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        with open(self.args.output, 'w') as f:
            json.dump(full_report, f, indent=2)
        
        print(f"\nReport saved to: {self.args.output}") 