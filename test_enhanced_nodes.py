#!/usr/bin/env python3
"""
增强节点测试脚本

用于快速测试新增的4个增强节点：
1. MultiReferenceCharacterNode - 多参考图角色节点
2. CharacterConsistencyValidator - 一致性验证节点
3. KeyframeControllerNode - 关键帧控制节点
4. CameraMotionDesigner - 运镜设计节点
"""

import sys
import os

# 添加节点路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nodes.video_enhanced_nodes import (
    MultiReferenceCharacterNode,
    CharacterConsistencyValidator,
    KeyframeControllerNode,
    CameraMotionDesigner
)


def test_multi_reference_character_node():
    """测试多参考图角色节点"""
    print("\n" + "="*70)
    print("测试1: 多参考图角色节点 (MultiReferenceCharacterNode)")
    print("="*70)
    
    node = MultiReferenceCharacterNode()
    
    # 测试用例1: 完整参数
    print("\n测试用例1: 完整参数（3张参考图）")
    profile, summary, char_id = node.create_character_profile(
        character_name="李明",
        front_image="https://example.com/front.jpg",
        side_image="https://example.com/side.jpg",
        back_image="https://example.com/back.jpg",
        character_description="年轻男性，黑色短发，戴眼镜，身穿蓝色衬衫",
        gender="male",
        age_range="young_adult",
        style="cinematic"
    )
    
    print("\n角色ID:", char_id)
    print("\n特征摘要:")
    print(summary)
    print("\n一致性评分:", f"{profile['consistency_score']:.0%}")
    
    # 测试用例2: 最小参数
    print("\n" + "-"*70)
    print("测试用例2: 最小参数（1张参考图）")
    profile2, summary2, char_id2 = node.create_character_profile(
        character_name="小红",
        front_image="https://example.com/front.jpg"
    )
    
    print("\n角色ID:", char_id2)
    print("\n一致性评分:", f"{profile2['consistency_score']:.0%}")


def test_consistency_validator():
    """测试一致性验证节点"""
    print("\n" + "="*70)
    print("测试2: 一致性验证节点 (CharacterConsistencyValidator)")
    print("="*70)
    
    node = CharacterConsistencyValidator()
    
    # 创建测试用的角色配置
    test_profile = {
        "name": "李明",
        "reference_images": ["img1.jpg", "img2.jpg", "img3.jpg"],
        "consistency_score": 0.85,
        "features": {
            "gender": "male",
            "hair_color": "黑色"
        }
    }
    
    # 测试用例1: 达标情况
    print("\n测试用例1: 一致性评分达标 (0.85 > 0.75)")
    video_url, score, is_consistent, suggestions = node.validate_consistency(
        video_url="https://example.com/video.mp4",
        character_profile=test_profile,
        min_consistency_score=0.75
    )
    
    print("\n一致性评分:", f"{score:.0%}")
    print("是否达标:", "✅ 是" if is_consistent else "❌ 否")
    print("\n建议:")
    print(suggestions)
    
    # 测试用例2: 不达标情况
    print("\n" + "-"*70)
    print("测试用例2: 一致性评分不达标 (0.65 < 0.75)")
    test_profile_low = {
        **test_profile,
        "consistency_score": 0.60,
        "reference_images": ["img1.jpg"]  # 只有1张参考图
    }
    
    video_url2, score2, is_consistent2, suggestions2 = node.validate_consistency(
        video_url="https://example.com/video.mp4",
        character_profile=test_profile_low,
        min_consistency_score=0.75
    )
    
    print("\n一致性评分:", f"{score2:.0%}")
    print("是否达标:", "✅ 是" if is_consistent2 else "❌ 否")
    print("\n建议:")
    print(suggestions2)


def test_keyframe_controller():
    """测试关键帧控制节点"""
    print("\n" + "="*70)
    print("测试3: 关键帧控制节点 (KeyframeControllerNode)")
    print("="*70)
    
    node = KeyframeControllerNode()
    
    # 测试用例1: 首帧控制
    print("\n测试用例1: 首帧控制")
    params, summary = node.create_keyframe_params(
        prompt="李明在公园散步，阳光洒在他身上",
        start_frame="https://example.com/start.jpg",
        transition_type="smooth",
        motion_intensity=0.5
    )
    
    print("\n参数摘要:")
    print(summary)
    
    # 测试用例2: 首尾帧控制
    print("\n" + "-"*70)
    print("测试用例2: 首尾帧控制")
    params2, summary2 = node.create_keyframe_params(
        prompt="李明从站立慢慢坐下",
        start_frame="https://example.com/standing.jpg",
        end_frame="https://example.com/sitting.jpg",
        transition_type="ease_in_out",
        motion_intensity=0.7
    )
    
    print("\n参数摘要:")
    print(summary2)


def test_camera_motion_designer():
    """测试运镜设计节点"""
    print("\n" + "="*70)
    print("测试4: 运镜设计节点 (CameraMotionDesigner)")
    print("="*70)
    
    node = CameraMotionDesigner()
    
    # 测试用例1: 跟拍镜头
    print("\n测试用例1: 跟拍镜头")
    motion, summary = node.design_motion(
        motion_type="tracking",
        motion_speed=1.0,
        motion_intensity=0.5
    )
    
    print("\n运镜摘要:")
    print(summary)
    
    # 测试用例2: 推镜
    print("\n" + "-"*70)
    print("测试用例2: 推镜")
    motion2, summary2 = node.design_motion(
        motion_type="zoom_in",
        motion_speed=1.5,
        motion_intensity=0.8
    )
    
    print("\n运镜摘要:")
    print(summary2)
    
    # 测试用例3: 环绕镜头
    print("\n" + "-"*70)
    print("测试用例3: 环绕镜头")
    motion3, summary3 = node.design_motion(
        motion_type="orbit",
        motion_speed=0.8,
        motion_intensity=0.6
    )
    
    print("\n运镜摘要:")
    print(summary3)


def main():
    """运行所有测试"""
    print("\n" + "🎬 "*20)
    print("ComfyUI 视频生成增强节点测试")
    print("🎬 "*20)
    
    try:
        # 测试各个节点
        test_multi_reference_character_node()
        test_consistency_validator()
        test_keyframe_controller()
        test_camera_motion_designer()
        
        print("\n" + "="*70)
        print("✅ 所有测试完成！")
        print("="*70)
        print("\n下一步:")
        print("1. 重启 ComfyUI: cd ~/ComfyUI && python main.py")
        print("2. 访问界面: http://localhost:8188")
        print("3. 在节点菜单中找到新增的4个节点")
        print("4. 创建工作流并测试实际效果")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
