#!/usr/bin/env python3
"""
小说转漫剧快速入门脚本
Quick Start Script for Novel to Drama Workflow

使用方法:
1. 设置环境变量: export UNLIMITAI_API_KEY="your-api-key"
2. 运行脚本: python quick_start.py
3. 查看输出: manifest.json
"""

import sys
import os
import json
import time

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nodes.text_nodes import NovelAnalyzerNode
from nodes.image_nodes import FluxProNode
from nodes.video_nodes import KlingImageToVideoNode
from nodes.audio_nodes import MinimaxTTSNode, BackgroundMusicGeneratorNode
from nodes.workflow_nodes import DramaManifestNode


def main():
    print("=" * 60)
    print("小说转漫剧快速入门脚本")
    print("Novel to Drama Quick Start Script")
    print("=" * 60)
    
    # 1. 获取 API Key
    api_key = os.environ.get("UNLIMITAI_API_KEY", "")
    if not api_key:
        print("\n⚠️  请设置环境变量 UNLIMITAI_API_KEY")
        print("   export UNLIMITAI_API_KEY='your-api-key'")
        print("\n或者在下方输入您的 API Key:")
        api_key = input("API Key: ").strip()
        
        if not api_key:
            print("❌ API Key 不能为空")
            return
    
    print(f"\n✓ API Key: {api_key[:10]}...")
    
    # 2. 输入小说文本
    print("\n" + "=" * 60)
    print("步骤 1: 输入小说文本")
    print("=" * 60)
    
    sample_novel = """
第一章 相遇

春日的阳光透过梧桐树叶洒落在街道上，林晓薇匆匆走在去公司的路上。
她没注意到，一辆黑色轿车正缓缓驶来...

"小心！"

一个低沉的男声响起，林晓薇被拉入一个温暖的怀抱。她抬头，看到
一双深邃的眼眸。

"你没事吧？"男人关切地问道。

林晓薇愣住了，这个男人有着俊朗的面容..."我叫陆晨轩。"

这一刻，命运的齿轮开始转动...
    """.strip()
    
    print("\n示例小说:")
    print(sample_novel)
    
    use_sample = input("\n使用示例小说？(y/n，默认 y): ").strip().lower()
    
    if use_sample != 'n':
        novel_text = sample_novel
    else:
        print("\n请粘贴您的小说文本（输入空行结束）:")
        lines = []
        while True:
            line = input()
            if line == "":
                break
            lines.append(line)
        novel_text = "\n".join(lines)
    
    # 3. 配置参数
    print("\n" + "=" * 60)
    print("步骤 2: 配置参数")
    print("=" * 60)
    
    num_scenes = input("场景数量 (1-20，默认 5): ").strip()
    num_scenes = int(num_scenes) if num_scenes else 5
    
    print(f"\n✓ 场景数量: {num_scenes}")
    
    # 4. 分析小说
    print("\n" + "=" * 60)
    print("步骤 3: 分析小说提取场景")
    print("=" * 60)
    
    analyzer = NovelAnalyzerNode()
    
    print("正在分析小说...")
    start_time = time.time()
    
    scenes_json, summary, cost = analyzer.analyze(
        api_key=api_key,
        novel_text=novel_text,
        num_scenes=num_scenes,
        model="deepseek-chat",
        language="chinese"
    )
    
    elapsed = time.time() - start_time
    print(f"\n✓ 分析完成 (耗时 {elapsed:.1f} 秒)")
    print(f"✓ 预估成本: {cost}")
    print(f"\n剧情概要:\n{summary}")
    
    scenes_data = json.loads(scenes_json)
    print(f"\n提取了 {len(scenes_data.get('scenes', []))} 个场景")
    
    # 询问是否继续
    print("\n" + "-" * 60)
    continue_generate = input("是否继续生成图像和视频？(y/n，默认 n): ").strip().lower()
    
    if continue_generate != 'y':
        print("\n✓ 已保存场景数据到 scenes.json")
        with open('scenes.json', 'w', encoding='utf-8') as f:
            f.write(scenes_json)
        print("✓ 完成！您可以稍后继续处理")
        return
    
    # 5. 生成图像
    print("\n" + "=" * 60)
    print("步骤 4: 批量生成场景图像")
    print("=" * 60)
    
    from nodes.workflow_nodes import SceneImageGeneratorNode
    
    image_gen = SceneImageGeneratorNode()
    
    print(f"正在生成 {num_scenes} 张图像...")
    start_time = time.time()
    
    images_json, img_summary = image_gen.generate(
        api_key=api_key,
        scenes_json=scenes_json,
        image_model="flux-pro",
        aspect_ratio="16:9",
        max_scenes=num_scenes
    )
    
    elapsed = time.time() - start_time
    print(f"\n✓ 图像生成完成 (耗时 {elapsed:.1f} 秒)")
    print(f"✓ {img_summary}")
    
    # 6. 生成视频
    print("\n" + "=" * 60)
    print("步骤 5: 批量生成场景视频")
    print("=" * 60)
    
    from nodes.workflow_nodes import SceneVideoGeneratorNode
    
    video_gen = SceneVideoGeneratorNode()
    
    print(f"正在生成 {num_scenes} 个视频...")
    print("⚠️  这可能需要 5-15 分钟，请耐心等待...")
    start_time = time.time()
    
    videos_json, vid_summary = video_gen.generate(
        api_key=api_key,
        images_json=images_json,
        video_model="kling-v2",
        duration="5",
        aspect_ratio="16:9"
    )
    
    elapsed = time.time() - start_time
    print(f"\n✓ 视频生成完成 (耗时 {elapsed:.1f} 秒)")
    print(f"✓ {vid_summary}")
    
    # 7. 生成音频
    print("\n" + "=" * 60)
    print("步骤 6: 批量生成音频")
    print("=" * 60)
    
    from nodes.workflow_nodes import SceneAudioGeneratorNode
    
    audio_gen = SceneAudioGeneratorNode()
    
    print(f"正在生成对话配音和背景音乐...")
    start_time = time.time()
    
    audio_json, audio_summary = audio_gen.generate(
        api_key=api_key,
        scenes_json=scenes_json,
        voice_id="male-qn-jingying",
        generate_music=True,
        max_scenes=num_scenes
    )
    
    elapsed = time.time() - start_time
    print(f"\n✓ 音频生成完成 (耗时 {elapsed:.1f} 秒)")
    print(f"✓ {audio_summary}")
    
    # 8. 整合资源
    print("\n" + "=" * 60)
    print("步骤 7: 整合所有资源")
    print("=" * 60)
    
    manifest_gen = DramaManifestNode()
    
    manifest_json, manifest_summary = manifest_gen.create_manifest(
        scenes_json=scenes_json,
        images_json=images_json,
        videos_json=videos_json,
        audio_json=audio_json,
        title="我的漫剧作品"
    )
    
    print(f"\n✓ {manifest_summary}")
    
    # 9. 保存结果
    print("\n" + "=" * 60)
    print("完成！")
    print("=" * 60)
    
    # 保存所有文件
    with open('scenes.json', 'w', encoding='utf-8') as f:
        f.write(scenes_json)
    
    with open('images.json', 'w', encoding='utf-8') as f:
        f.write(images_json)
    
    with open('videos.json', 'w', encoding='utf-8') as f:
        f.write(videos_json)
    
    with open('audio.json', 'w', encoding='utf-8') as f:
        f.write(audio_json)
    
    with open('manifest.json', 'w', encoding='utf-8') as f:
        f.write(manifest_json)
    
    print("\n✓ 已保存以下文件:")
    print("  - scenes.json    (场景数据)")
    print("  - images.json    (图像资源)")
    print("  - videos.json    (视频资源)")
    print("  - audio.json     (音频资源)")
    print("  - manifest.json  (完整清单)")
    
    # 显示 manifest 示例
    manifest_data = json.loads(manifest_json)
    print(f"\nManifest 示例 (第 1 个场景):")
    if manifest_data.get("scenes"):
        first_scene = manifest_data["scenes"][0]
        print(json.dumps(first_scene, ensure_ascii=False, indent=2))
    
    print("\n" + "=" * 60)
    print("🎉 恭喜！您的漫剧已生成完成！")
    print("=" * 60)
    
    print("\n下一步:")
    print("1. 查看 manifest.json 获取所有资源链接")
    print("2. 下载图像、视频、音频文件")
    print("3. 使用视频编辑软件合成最终作品")
    print("4. 或使用 ComfyUI 工作流进一步处理")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
    except Exception as e:
        print(f"\n\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
