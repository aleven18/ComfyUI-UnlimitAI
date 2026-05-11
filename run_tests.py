#!/usr/bin/env python3
"""
测试运行脚本

用法:
    # 运行所有单元测试
    python run_tests.py
    
    # 运行慢速测试
    python run_tests.py --run-slow
    
    # 运行API测试
    python run_tests.py --run-api
    
    # 运行特定测试文件
    python run_tests.py tests/test_api_client.py
    
    # 生成覆盖率报告
    python run_tests.py --cov-report=html
"""

import sys
import subprocess
from pathlib import Path


def main():
    """运行测试"""
    # 确定pytest命令
    pytest_cmd = [sys.executable, "-m", "pytest"]
    
    # 添加默认参数
    pytest_cmd.extend([
        "tests/",
        "-v",
        "--tb=short",
        "--strict-markers",
        "-p", "no:warnings"
    ])
    
    # 解析命令行参数
    args = sys.argv[1:]
    
    if "--run-slow" in args:
        pytest_cmd.append("--run-slow")
        args.remove("--run-slow")
    
    if "--run-api" in args:
        pytest_cmd.append("--run-api")
        args.remove("--run-api")
    
    if "--run-integration" in args:
        pytest_cmd.append("--run-integration")
        args.remove("--run-integration")
    
    if "--cov-report=html" in args:
        pytest_cmd.extend([
            "--cov=.",
            "--cov-report=html:htmlcov",
            "--cov-report=term-missing"
        ])
        args.remove("--cov-report=html")
    
    # 添加其他参数
    pytest_cmd.extend(args)
    
    # 运行测试
    print(f"运行命令: {' '.join(pytest_cmd)}")
    print("=" * 80)
    
    result = subprocess.run(pytest_cmd)
    
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
