#!/usr/bin/env python3
"""检查工作流文件完整性"""

import json
import sys
from pathlib import Path

# 已知的节点类型
KNOWN_NODES = {
    "DramaConfigNode",
    "CostEstimatorNode",
    "NovelToDramaWorkflowNode",
    "SceneImageGeneratorNode",
    "SceneVideoGeneratorNode",
    "SceneAudioGeneratorNode",
    "DramaManifestNode",
    "Note",
    "Reroute"  # ComfyUI内置节点
}

# 配置文件映射
CONFIG_MAP = {
    "budget_workflow.json": "budget_config.json",
    "balanced_workflow.json": "balanced_config.json",
    "quality_workflow.json": "quality_config.json",
    "max_quality_workflow.json": "max_quality_config.json"
}

def check_workflow(workflow_file):
    """检查单个工作流文件"""
    print(f"\n{'='*60}")
    print(f"检查: {workflow_file}")
    print(f"{'='*60}")
    
    issues = []
    
    # 读取工作流文件
    with open(workflow_file) as f:
        workflow = json.load(f)
    
    # 检查必要字段
    required_fields = ["nodes", "links", "groups", "version"]
    for field in required_fields:
        if field not in workflow:
            issues.append(f"❌ 缺少字段: {field}")
    
    # 检查节点
    print(f"\n节点数量: {len(workflow.get('nodes', []))}")
    
    node_types = set()
    for node in workflow.get('nodes', []):
        node_type = node.get('type')
        node_types.add(node_type)
        
        if node_type not in KNOWN_NODES:
            issues.append(f"⚠️  未知节点类型: {node_type}")
        
        # 检查节点ID
        if 'id' not in node:
            issues.append(f"❌ 节点缺少ID: {node_type}")
        
        # 检查位置和大小
        if 'pos' not in node:
            issues.append(f"⚠️  节点缺少位置: {node_type} (id={node.get('id')})")
        if 'size' not in node:
            issues.append(f"⚠️  节点缺少大小: {node_type} (id={node.get('id')})")
    
    print(f"节点类型: {', '.join(sorted(node_types))}")
    
    # 检查链接
    print(f"\n链接数量: {len(workflow.get('links', []))}")
    
    node_ids = {node['id'] for node in workflow.get('nodes', [])}
    
    for link in workflow.get('links', []):
        if len(link) < 5:
            issues.append(f"❌ 链接格式错误: {link}")
            continue
        
        link_id, from_node, from_slot, to_node, to_slot = link[:5]
        
        if from_node not in node_ids:
            issues.append(f"❌ 链接 {link_id}: 源节点 {from_node} 不存在")
        if to_node not in node_ids:
            issues.append(f"❌ 链接 {link_id}: 目标节点 {to_node} 不存在")
    
    # 检查配置一致性
    workflow_name = Path(workflow_file).name
    if workflow_name in CONFIG_MAP:
        config_file = Path(workflow_file).parent.parent / "workflow_configs" / CONFIG_MAP[workflow_name]
        
        if config_file.exists():
            with open(config_file) as f:
                config = json.load(f)
            
            print(f"\n配置文件: {CONFIG_MAP[workflow_name]}")
            print(f"预期成本: ${config.get('estimated_cost', 'N/A')}")
            print(f"预期时间: {config.get('estimated_time', 'N/A')}")
            print(f"质量等级: {config.get('quality_level', 'N/A')}/5")
            
            # 检查DramaConfigNode的参数
            for node in workflow.get('nodes', []):
                if node.get('type') == 'DramaConfigNode':
                    widgets = node.get('widgets_values', [])
                    
                    # 检查模型配置
                    if len(widgets) >= 20:
                        text_model = widgets[3]
                        image_model = widgets[6]
                        video_model = widgets[8]
                        
                        expected_text = config['models']['text']['model']
                        expected_image = config['models']['image']['model']
                        expected_video = config['models']['video']['model']
                        
                        if text_model != expected_text:
                            issues.append(f"⚠️  文本模型不匹配: {text_model} != {expected_text}")
                        if image_model != expected_image:
                            issues.append(f"⚠️  图像模型不匹配: {image_model} != {expected_image}")
                        if video_model != expected_video:
                            issues.append(f"⚠️  视频模型不匹配: {video_model} != {expected_video}")
        else:
            issues.append(f"⚠️  配置文件不存在: {config_file}")
    
    # 输出问题
    if issues:
        print(f"\n发现 {len(issues)} 个问题:")
        for issue in issues:
            print(f"  {issue}")
        return False
    else:
        print(f"\n✅ 工作流检查通过")
        return True

def main():
    """主函数"""
    workflows_dir = Path(__file__).parent / "workflows"
    
    print("ComfyUI-UnlimitAI 工作流检查工具")
    print("="*60)
    
    all_passed = True
    
    for workflow_file in workflows_dir.glob("*_workflow.json"):
        if not check_workflow(workflow_file):
            all_passed = False
    
    print(f"\n{'='*60}")
    if all_passed:
        print("✅ 所有工作流检查通过")
        return 0
    else:
        print("❌ 部分工作流存在问题")
        return 1

if __name__ == "__main__":
    sys.exit(main())
