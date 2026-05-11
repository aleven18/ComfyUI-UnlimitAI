#!/usr/bin/env python3
"""
性能基准测试脚本

测试各种操作的执行时间和资源使用情况。

运行方式:
    python scripts/benchmark.py
"""

import time
import sys
import os
from pathlib import Path
import statistics
from typing import List, Callable

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.api_client import UnlimitAIClient
from utils.logger import get_logger
from utils.delay import SmartDelay

logger = get_logger("benchmark")


class BenchmarkRunner:
    """基准测试运行器"""
    
    def __init__(self):
        self.results = {}
    
    def run_benchmark(
        self,
        name: str,
        func: Callable,
        iterations: int = 3,
        warmup: int = 1
    ):
        """
        运行基准测试
        
        Args:
            name: 测试名称
            func: 要测试的函数
            iterations: 迭代次数
            warmup: 预热次数
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"基准测试: {name}")
        logger.info(f"{'='*60}")
        
        # 预热
        logger.info(f"预热 {warmup} 次...")
        for _ in range(warmup):
            try:
                func()
            except Exception as e:
                logger.warning(f"预热失败: {e}")
        
        # 正式测试
        logger.info(f"运行 {iterations} 次测试...")
        times = []
        
        for i in range(iterations):
            start = time.time()
            try:
                result = func()
                elapsed = time.time() - start
                times.append(elapsed)
                logger.info(f"  第 {i+1} 次: {elapsed:.2f}秒")
            except Exception as e:
                logger.error(f"  第 {i+1} 次失败: {e}")
        
        if times:
            self.results[name] = {
                'times': times,
                'avg': statistics.mean(times),
                'min': min(times),
                'max': max(times),
                'median': statistics.median(times),
                'stdev': statistics.stdev(times) if len(times) > 1 else 0
            }
            
            logger.info(f"\n统计结果:")
            logger.info(f"  平均: {self.results[name]['avg']:.2f}秒")
            logger.info(f"  最小: {self.results[name]['min']:.2f}秒")
            logger.info(f"  最大: {self.results[name]['max']:.2f}秒")
            logger.info(f"  中位数: {self.results[name]['median']:.2f}秒")
            logger.info(f"  标准差: {self.results[name]['stdev']:.2f}秒")
        else:
            logger.error("所有测试都失败了")
    
    def print_summary(self):
        """打印总结"""
        logger.info(f"\n{'='*60}")
        logger.info("基准测试总结")
        logger.info(f"{'='*60}")
        
        if not self.results:
            logger.warning("没有测试结果")
            return
        
        # 表头
        print(f"\n{'测试名称':<30} {'平均时间':<12} {'最小时间':<12} {'最大时间':<12}")
        print("-" * 66)
        
        # 结果
        for name, data in sorted(self.results.items()):
            print(f"{name:<30} {data['avg']:<12.2f} {data['min']:<12.2f} {data['max']:<12.2f}")
        
        print()


def benchmark_text_generation(client: UnlimitAIClient):
    """测试文本生成性能"""
    return client.generate_text(
        prompt="写一段描写春天的文字",
        model="deepseek-chat",
        max_tokens=100
    )


def benchmark_image_generation(client: UnlimitAIClient):
    """测试图像生成性能"""
    return client.generate_image(
        prompt="春天的花园",
        model="flux.1-schnell",
        size="512x512"
    )


def benchmark_delay_system():
    """测试延迟系统性能"""
    delay = SmartDelay(initial_delay=0.1)
    times = []
    
    for _ in range(10):
        start = time.time()
        delay.wait("test")
        elapsed = time.time() - start
        times.append(elapsed)
    
    return statistics.mean(times)


def main():
    """主函数"""
    api_key = os.getenv("UNITED_API_KEY")
    
    if not api_key:
        logger.error("未设置UNITED_API_KEY环境变量")
        logger.info("将跳过需要API的测试")
    
    runner = BenchmarkRunner()
    
    # 延迟系统测试（不需要API）
    runner.run_benchmark(
        "延迟系统",
        benchmark_delay_system,
        iterations=5
    )
    
    # API测试
    if api_key:
        client = UnlimitAIClient(api_key=api_key)
        
        runner.run_benchmark(
            "文本生成 (deepseek-chat)",
            lambda: benchmark_text_generation(client),
            iterations=3
        )
        
        runner.run_benchmark(
            "图像生成 (flux.1-schnell)",
            lambda: benchmark_image_generation(client),
            iterations=2
        )
    
    # 打印总结
    runner.print_summary()
    
    logger.info("基准测试完成！")


if __name__ == "__main__":
    main()
