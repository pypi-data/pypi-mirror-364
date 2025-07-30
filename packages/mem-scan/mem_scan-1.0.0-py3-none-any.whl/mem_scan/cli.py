#!/usr/bin/env python3
"""
CLI entry point for mem-scan tool
"""

import argparse
import sys
from .scanner import MemoryScanner


def main():
    """CLI 工具的主入口点"""
    parser = argparse.ArgumentParser(
        description="Monitor memory usage while executing a command",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  mem-scan python eval.py
  mem-scan --gpu-id 1 --interval 0.05 python train.py
  mem-scan --output report.json --quiet python inference.py
  mem-scan python -m modelopt.onnx.quantization --onnx_path=model.onnx --quantize_mode=fp8
        """
    )
    
    parser.add_argument(
        '--gpu-id',
        type=int,
        default=0,
        help='GPU device ID to monitor (default: 0)'
    )
    
    parser.add_argument(
        '--interval',
        type=float,
        default=0.1,
        help='Monitoring interval in seconds (default: 0.1)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        help='Save report to JSON file'
    )
    
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress command output'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='mem-scan 1.0.0'
    )
    
    # parse known args and let the rest pass through to the command
    args, unknown_args = parser.parse_known_args()
    
    # the command is everything that wasn't parsed by our parser
    if not unknown_args:
        parser.error("No command specified to monitor")
    
    command = unknown_args
    
    # run the scanner
    scanner = MemoryScanner(args, command)
    return scanner.run_command()


if __name__ == "__main__":
    sys.exit(main()) 