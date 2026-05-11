#!/usr/bin/env python3
"""
ComfyUI-UnlimitAI 基础使用示例

本示例展示如何使用UnlimitAI客户端进行基本的文本、图像、视频生成。

运行前请设置环境变量:
    export UNITED_API_KEY="your_api_key"
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.api_client import UnlimitAIClient
from utils.logger import get_logger
from utils.exceptions import APIError, ValidationError

# 初始化日志
logger = get_logger("basic_usage")


def example_text_generation(client: UnlimitAIClient):
    """
    示例：文本生成
    """
    logger.info("=" * 60)
    logger.info("示例1: 文本生成")
    logger.info("=" * 60)
    
    try:
        # 简单文本生成
        prompt = "写一段描写春天樱花盛开的文字"
        logger.info(f"提示词: {prompt}")
        
        text = client.generate_text(
            prompt=prompt,
            model="deepseek-chat"
        )
        
        logger.info(f"生成结果:\n{text}")
        logger.info("✓ 文本生成成功")
        
    except Exception as e:
        logger.error(f"✗ 文本生成失败: {e}", exc_info=True)


def example_image_generation(client: UnlimitAIClient):
    """
    示例：图像生成
    """
    logger.info("\n" + "=" * 60)
    logger.info("示例2: 图像生成")
    logger.info("=" * 60)
    
    try:
        prompt = "一个穿着蓝色碎花连衣裙的年轻女孩，站在樱花树下，微风拂过，花瓣飘落，温暖的午后阳光，日系动漫风格"
        logger.info(f"提示词: {prompt}")
        
        image_url = client.generate_image(
            prompt=prompt,
            model="flux.1-schnell",
            size="1024x1024"
        )
        
        logger.info(f"图像URL: {image_url}")
        logger.info("✓ 图像生成成功")
        
    except Exception as e:
        logger.error(f"✗ 图像生成失败: {e}", exc_info=True)


def example_video_generation(client: UnlimitAIClient):
    """
    示例：视频生成
    """
    logger.info("\n" + "=" * 60)
    logger.info("示例3: 视频生成")
    logger.info("=" * 60)
    
    try:
        prompt = "女孩在樱花树下旋转跳舞，裙摆飞扬，樱花花瓣随风飘舞"
        logger.info(f"提示词: {prompt}")
        
        video_url = client.generate_video(
            prompt=prompt,
            model="kling-video-v2",
            duration=5.0
        )
        
        logger.info(f"视频URL: {video_url}")
        logger.info("✓ 视频生成成功")
        
    except Exception as e:
        logger.error(f"✗ 视频生成失败: {e}", exc_info=True)


def example_audio_generation(client: UnlimitAIClient):
    """
    示例：音频生成
    """
    logger.info("\n" + "=" * 60)
    logger.info("示例4: 音频生成")
    logger.info("=" * 60)
    
    try:
        text = "春天的风吹过樱花树，带来了花香和希望。"
        logger.info(f"文本: {text}")
        
        audio_url = client.generate_audio(
            text=text,
            model="tts-1",
            voice="alloy"
        )
        
        logger.info(f"音频URL: {audio_url}")
        logger.info("✓ 音频生成成功")
        
    except Exception as e:
        logger.error(f"✗ 音频生成失败: {e}", exc_info=True)


def example_music_generation(client: UnlimitAIClient):
    """
    示例：音乐生成
    """
    logger.info("\n" + "=" * 60)
    logger.info("示例5: 音乐生成")
    logger.info("=" * 60)
    
    try:
        prompt = "轻快的钢琴曲，春天主题，适合樱花飘落的场景"
        logger.info(f"提示词: {prompt}")
        
        music_url = client.generate_music(
            prompt=prompt,
            model="musicgen",
            duration=30.0
        )
        
        logger.info(f"音乐URL: {music_url}")
        logger.info("✓ 音乐生成成功")
        
    except Exception as e:
        logger.error(f"✗ 音乐生成失败: {e}", exc_info=True)


def example_error_handling(client: UnlimitAIClient):
    """
    示例：错误处理
    """
    logger.info("\n" + "=" * 60)
    logger.info("示例6: 错误处理")
    logger.info("=" * 60)
    
    # 验证错误
    try:
        client.generate_text(prompt="")
    except ValidationError as e:
        logger.info(f"✓ 捕获到验证错误: {e}")
    
    # API错误示例
    try:
        # 故意使用无效模型
        client.generate_text(prompt="test", model="invalid-model")
    except APIError as e:
        logger.info(f"✓ 捕获到API错误: {e}")


def main():
    """
    主函数
    """
    # 检查API密钥
    api_key = os.getenv("UNITED_API_KEY")
    if not api_key:
        logger.error("未设置UNITED_API_KEY环境变量")
        logger.info("请运行: export UNITED_API_KEY='your_api_key'")
        sys.exit(1)
    
    # 初始化客户端
    logger.info("初始化UnlimitAI客户端...")
    client = UnlimitAIClient(api_key=api_key)
    
    # 运行示例
    example_text_generation(client)
    example_image_generation(client)
    example_video_generation(client)
    example_audio_generation(client)
    example_music_generation(client)
    example_error_handling(client)
    
    logger.info("\n" + "=" * 60)
    logger.info("所有示例运行完成！")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
