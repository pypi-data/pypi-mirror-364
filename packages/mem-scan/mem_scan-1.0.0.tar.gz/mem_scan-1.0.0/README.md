# mem-scan

一个用于监控系统和 GPU 内存使用情况的命令行工具，特别适用于监控 Python 程序执行期间的内存特征。

## 功能特性

- 实时监控 CPU 内存和 GPU 内存使用情况
- 支持监控任意命令的执行过程
- 提供峰值、最小值和平均值统计
- 支持将报告保存为 JSON 格式
- 可配置监控间隔和 GPU 设备
- 支持静默模式执行

## 安装

### 使用 uv 安装（推荐）

```bash
# 从源码安装
uv pip install -e .

# 或者直接安装
uv pip install mem-scan
```

### 使用 pip 安装

```bash
pip install -e .
```

## 依赖项

- `psutil>=5.8.0` - 系统内存监控
- `pynvml>=11.0.0` - GPU 内存监控

## 使用方法

### 基本用法

```bash
# 监控 Python 脚本执行
mem-scan python your_script.py

# 监控带参数的命令
mem-scan python train.py --batch-size 128 --epochs 10

# 监控模型量化过程
mem-scan python -m modelopt.onnx.quantization --onnx_path=model.onnx --quantize_mode=fp8
```

### 高级选项

```bash
# 指定 GPU 设备
mem-scan --gpu-id 1 python eval.py

# 调整监控间隔（秒）
mem-scan --interval 0.05 python train.py

# 保存报告到文件
mem-scan --output memory_report.json python inference.py

# 静默模式（不显示命令输出）
mem-scan --quiet --output report.json python benchmark.py

# 查看版本信息
mem-scan --version

# 查看帮助信息
mem-scan --help
```

## 输出示例

```
Starting memory monitoring for: python train.py --batch-size 128
GPU ID: 0, Interval: 0.1s
------------------------------------------------------------

============================================================
MEMORY USAGE REPORT
============================================================
Execution Time: 45.32 seconds
Return Code: 0

GPU Memory Usage:
  Peak: 8.45 GB
  Min:  0.12 GB
  Avg:  6.78 GB

Host Memory Usage:
  Peak: 12.34 GB
  Min:  8.90 GB
  Avg:  10.45 GB

Report saved to: memory_report.json
```

## JSON 报告格式

当使用 `--output` 选项时，会生成包含详细信息的 JSON 报告：

```json
{
  "execution_time": 45.32,
  "return_code": 0,
  "memory_usage": {
    "gpu_peak_gb": 8.45,
    "gpu_min_gb": 0.12,
    "gpu_avg_gb": 6.78,
    "host_peak_gb": 12.34,
    "host_min_gb": 8.90,
    "host_avg_gb": 10.45
  },
  "command": "python train.py --batch-size 128",
  "timestamp": "2024-01-20 14:30:45"
}
```

## 开发

### 开发环境设置

```bash
# 克隆仓库
git clone <repository-url>
cd mem_scan

# 使用 uv 安装开发依赖
uv pip install -e ".[dev]"

# 运行测试
pytest

# 代码格式化
black src/ tests/

# 类型检查
mypy src/
```

### 构建和发布

```bash
# 构建包
uv build

# 发布到 PyPI（需要配置认证）
uv publish
```

## 注意事项

1. GPU 监控需要安装 NVIDIA 驱动和 `pynvml` 库
2. 如果没有 GPU 或无法初始化 GPU 监控，工具会显示警告但仍会监控 CPU 内存
3. 监控间隔设置过小可能会影响被监控程序的性能
4. 使用 `--quiet` 模式时，被监控程序的输出会被捕获但不显示

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！ 