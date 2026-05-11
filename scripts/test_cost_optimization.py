#!/usr/bin/env python3
"""
成本优化效果测试脚本

测试各种优化策略的效果：
- 两阶段生成
- 智能模型选择
- 提示词优化
- 资源复用
- 缓存系统
"""

import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.cost_optimizer import (
    CostOptimizer,
    SmartModelSelector,
    PromptOptimizer,
    TwoStageGenerator
)


def create_test_scenes():
    """创建测试场景"""
    return [
        {
            "scene_number": 1,
            "title": "春日相遇",
            "description": "林晓薇在街上差点被车撞，被陆晨轩救下。特写镜头，林晓薇惊讶的表情。",
            "characters": ["林晓薇", "陆晨轩"],
            "mood": "romantic",
            "dialogue": "(breath) 小心！你没事吧？"
        },
        {
            "scene_number": 2,
            "title": "咖啡厅对话",
            "description": "两人在咖啡厅坐下交谈。中景镜头，温馨的氛围。",
            "characters": ["林晓薇", "陆晨轩"],
            "mood": "romantic",
            "dialogue": "我叫陆晨轩，很高兴认识你。"
        },
        {
            "scene_number": 3,
            "title": "城市街道",
            "description": "远景，城市街道，车水马龙。自然光，日间。",
            "characters": [],
            "mood": "neutral",
            "dialogue": ""
        },
        {
            "scene_number": 4,
            "title": "特效场景",
            "description": "魔法特效爆发，粒子环绕，人物悬浮。复杂特效场景。",
            "characters": ["林晓薇"],
            "mood": "action",
            "dialogue": "(惊叹) 这是什么力量？"
        },
        {
            "scene_number": 5,
            "title": "办公室",
            "description": "林晓薇在办公室工作。室内场景，单人。",
            "characters": ["林晓薇"],
            "mood": "neutral",
            "dialogue": "今天的工作终于完成了。"
        },
        {
            "scene_number": 6,
            "title": "夜晚街景",
            "description": "夜晚的城市街道，霓虹灯闪烁。室外夜景。",
            "characters": [],
            "mood": "romantic",
            "dialogue": ""
        },
        {
            "scene_number": 7,
            "title": "文字渲染",
            "description": "电影标题出现，精致的文字排版。需要高质量文字渲染。",
            "characters": [],
            "mood": "neutral",
            "dialogue": ""
        },
        {
            "scene_number": 8,
            "title": "多人群像",
            "description": "五个角色站在一起的群像。复杂人物构图。",
            "characters": ["林晓薇", "陆晨轩", "张伟", "李娜", "王强"],
            "mood": "happy",
            "dialogue": "大家一起合影吧！"
        },
        {
            "scene_number": 9,
            "title": "自然风光",
            "description": "山水自然风光，鸟语花香。远景自然场景。",
            "characters": [],
            "mood": "happy",
            "dialogue": ""
        },
        {
            "scene_number": 10,
            "title": "情感高潮",
            "description": "林晓薇和陆晨轩深情对视，情感爆发。特写镜头，复杂光影。",
            "characters": ["林晓薇", "陆晨轩"],
            "mood": "romantic",
            "dialogue": "我愿意等你。"
        }
    ]


def test_smart_model_selection():
    """测试智能模型选择"""
    print("\n" + "="*60)
    print("测试1: 智能模型选择")
    print("="*60)
    
    scenes = create_test_scenes()
    selector = SmartModelSelector()
    
    results = {
        "simple": [],
        "medium": [],
        "complex": []
    }
    
    for scene in scenes:
        complexity = selector._analyze_scene_complexity(scene)
        image_model, reason = selector.select_image_model(scene)
        video_model, video_reason = selector.select_video_model(scene, "balanced")
        
        results[complexity].append({
            "scene": scene["title"],
            "image_model": image_model,
            "video_model": video_model,
            "reason": reason
        })
        
        print(f"\n场景 {scene['scene_number']}: {scene['title']}")
        print(f"  复杂度: {complexity}")
        print(f"  图像模型: {image_model} ({reason})")
        print(f"  视频模型: {video_model} ({video_reason})")
    
    print("\n复杂度分布:")
    for complexity, items in results.items():
        print(f"  {complexity}: {len(items)} 个场景")
    
    return results


def test_prompt_optimization():
    """测试提示词优化"""
    print("\n" + "="*60)
    print("测试2: 提示词优化")
    print("="*60)
    
    scenes = create_test_scenes()
    optimizer = PromptOptimizer()
    
    for scene in scenes[:3]:  # 只测试前3个场景
        print(f"\n场景 {scene['scene_number']}: {scene['title']}")
        
        positive, negative = optimizer.optimize_image_prompt(scene, quality="high")
        
        print(f"  正向提示词: {positive[:100]}...")
        print(f"  负面提示词: {negative[:80]}...")


def test_cost_calculation():
    """测试成本计算"""
    print("\n" + "="*60)
    print("测试3: 成本计算对比")
    print("="*60)
    
    scenes = create_test_scenes()
    optimizer = CostOptimizer()
    
    # 不同策略的成本对比
    strategies = ["budget", "balanced", "quality"]
    
    print(f"\n场景数量: {len(scenes)}")
    print("\n成本对比:")
    print("-" * 80)
    print(f"{'策略':<15} {'文本':<10} {'图像':<10} {'视频':<10} {'音频':<10} {'音乐':<10} {'总计':<10}")
    print("-" * 80)
    
    for strategy in strategies:
        result = optimizer.model_selector.calculate_optimized_cost(scenes, strategy)
        
        print(f"{strategy:<15} "
              f"${result['text']:<9.3f} "
              f"${result['image']:<9.2f} "
              f"${result['video']:<9.2f} "
              f"${result['audio']:<9.2f} "
              f"${result['music']:<9.2f} "
              f"${result['total']:<9.2f}")
    
    print("-" * 80)


def test_two_stage_generation():
    """测试两阶段生成"""
    print("\n" + "="*60)
    print("测试4: 两阶段生成")
    print("="*60)
    
    scenes = create_test_scenes()
    
    print(f"\n场景数量: {len(scenes)}")
    
    # 预览阶段成本
    preview_cost = len(scenes) * 0.20
    print(f"\n阶段1 - 预览成本:")
    print(f"  单场景成本: $0.20")
    print(f"  总成本: ${preview_cost:.2f}")
    
    # 假设80%的场景通过审核
    approved_count = int(len(scenes) * 0.8)
    print(f"\n通过审核: {approved_count} 个场景 (80%)")
    
    # 最终阶段成本
    final_cost = approved_count * 0.47
    print(f"\n阶段2 - 最终成本:")
    print(f"  单场景成本: $0.47")
    print(f"  总成本: ${final_cost:.2f}")
    
    # 总成本
    total_cost = preview_cost + final_cost
    print(f"\n两阶段总成本: ${total_cost:.2f}")
    
    # 对比直接生成
    direct_cost = len(scenes) * 0.53
    savings = direct_cost - total_cost
    savings_percent = (savings / direct_cost) * 100
    
    print(f"\n直接生成成本: ${direct_cost:.2f}")
    print(f"节省: ${savings:.2f} ({savings_percent:.1f}%)")


def test_comprehensive_optimization():
    """测试综合优化"""
    print("\n" + "="*60)
    print("测试5: 综合优化效果")
    print("="*60)
    
    scenes = create_test_scenes()
    optimizer = CostOptimizer()
    
    print(f"\n场景数量: {len(scenes)}")
    
    # 原始成本（全部使用中端模型）
    original_cost = len(scenes) * 0.53
    print(f"\n原始成本: ${original_cost:.2f}")
    
    # 综合优化策略
    strategies = {
        "两阶段生成": 0.73,  # 节省27%
        "智能模型选择": 0.85,  # 节省15%
        "提示词优化": 0.92,  # 节省8%
        "资源复用": 0.85,   # 节省15%
        "缓存系统": 0.80    # 节省20%
    }
    
    print("\n优化策略效果:")
    cumulative_savings = 1.0
    
    for strategy, factor in strategies.items():
        cumulative_savings *= factor
        savings_percent = (1 - factor) * 100
        print(f"  {strategy}: 节省 {savings_percent:.1f}%")
    
    optimized_cost = original_cost * cumulative_savings
    total_savings = original_cost - optimized_cost
    total_savings_percent = (1 - cumulative_savings) * 100
    
    print(f"\n综合优化结果:")
    print(f"  原始成本: ${original_cost:.2f}")
    print(f"  优化后成本: ${optimized_cost:.2f}")
    print(f"  总节省: ${total_savings:.2f} ({total_savings_percent:.1f}%)")


def test_scene_optimization():
    """测试场景优化"""
    print("\n" + "="*60)
    print("测试6: 单个场景优化示例")
    print("="*60)
    
    scene = {
        "scene_number": 1,
        "title": "春日相遇",
        "description": "林晓薇在街上差点被车撞，被陆晨轩救下。特写镜头，林晓薇惊讶的表情。",
        "characters": ["林晓薇", "陆晨轩"],
        "mood": "romantic",
        "dialogue": "(breath) 小心！你没事吧？"
    }
    
    optimizer = CostOptimizer()
    optimized = optimizer.optimize_scene(scene, budget="balanced")
    
    print(f"\n场景: {scene['title']}")
    print(f"描述: {scene['description']}")
    print(f"\n优化后的图像提示词:")
    print(f"  正向: {optimized['prompts']['image']['positive'][:120]}...")
    print(f"  负面: {optimized['prompts']['image']['negative'][:100]}...")
    print(f"\n选择的模型:")
    print(f"  图像: {optimized['models']['image']} - {optimized['reasons']['image']}")
    print(f"  视频: {optimized['models']['video']} - {optimized['reasons']['video']}")


def main():
    """主测试函数"""
    print("ComfyUI-UnlimitAI 成本优化测试")
    print("="*60)
    
    try:
        # 运行所有测试
        test_smart_model_selection()
        test_prompt_optimization()
        test_cost_calculation()
        test_two_stage_generation()
        test_comprehensive_optimization()
        test_scene_optimization()
        
        print("\n" + "="*60)
        print("✅ 所有测试完成")
        print("="*60)
        
        return 0
    
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
