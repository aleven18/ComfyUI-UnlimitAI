#!/usr/bin/env python3
"""
ComfyUI-UnlimitAI CLI工具

命令行界面，用于批量操作和自动化任务。

Usage:
    python cli.py --help
    python cli.py generate --prompt "..." --model "deepseek-chat"
    python cli.py batch --file prompts.txt
"""

import argparse
import sys
import os
from pathlib import Path
import json
import logging

sys.path.insert(0, str(Path(__file__).parent))

from utils.api_client import UnlimitAIClient
from utils.logger import get_logger

logger = get_logger("cli")


class CLI:
    """命令行工具类"""
    
    def __init__(self):
        self.client = None
        self._init_client()
    
    def _init_client(self):
        """初始化客户端"""
        api_key = os.getenv("UNITED_API_KEY")
        if not api_key:
            logger.error("未设置UNITED_API_KEY环境变量")
            sys.exit(1)
        self.client = UnlimitAIClient(api_key=api_key)
    
    def generate_text(self, args):
        """生成文本"""
        logger.info(f"生成文本: {args.prompt}")
        result = self.client.generate_text(
            prompt=args.prompt,
            model=args.model
        )
        print(result)
    
    def generate_image(self, args):
        """生成图像"""
        logger.info(f"生成图像: {args.prompt}")
        result = self.client.generate_image(
            prompt=args.prompt,
            model=args.model,
            size=args.size
        )
        print(f"图像URL: {result}")
    
    def batch(self, args):
        """批量处理"""
        logger.info(f"批量处理: {args.file}")
        
        with open(args.file, 'r') as f:
            prompts = [line.strip() for line in f if line.strip()]
        
        results = []
        for i, prompt in enumerate(prompts, 1):
            logger.info(f"处理 {i}/{len(prompts)}: {prompt}")
            result = self.client.generate_text(prompt)
            results.append({"prompt": prompt, "result": result})
        
        # 保存结果
        output_file = args.output or "batch_results.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"结果已保存到: {output_file}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="ComfyUI-UnlimitAI CLI工具",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # 文本生成命令
    text_parser = subparsers.add_parser("text", help="生成文本")
    text_parser.add_argument("--prompt", required=True, help="提示词")
    text_parser.add_argument("--model", default="deepseek-chat", help="模型")
    text_parser.set_defaults(func="generate_text")
    
    # 图像生成命令
    image_parser = subparsers.add_parser("image", help="生成图像")
    image_parser.add_argument("--prompt", required=True, help="提示词")
    image_parser.add_argument("--model", default="flux.1-schnell", help="模型")
    image_parser.add_argument("--size", default="1024x1024", help="尺寸")
    image_parser.set_defaults(func="generate_image")
    
    # 批处理命令
    batch_parser = subparsers.add_parser("batch", help="批量处理")
    batch_parser.add_argument("--file", required=True, help="提示词文件")
    batch_parser.add_argument("--output", help="输出文件")
    batch_parser.set_defaults(func="batch")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(0)
    
    cli = CLI()
    
    if hasattr(args, 'func'):
        method = getattr(cli, args.func)
        method(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
