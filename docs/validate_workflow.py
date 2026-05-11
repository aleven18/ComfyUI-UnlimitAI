#!/usr/bin/env python3
"""
验证工作流 JSON 格式是否符合 ComfyUI 要求
"""

import json
import sys

def validate_comfyui_workflow(filepath):
    """验证 ComfyUI 工作流 JSON"""
    
    print(f"验证工作流: {filepath}")
    print("=" * 60)
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            workflow = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ JSON 格式错误: {e}")
        return False
    
    # 检查必需字段
    required_fields = ['last_node_id', 'last_link_id', 'nodes', 'links']
    for field in required_fields:
        if field not in workflow:
            print(f"❌ 缺少必需字段: {field}")
            return False
        else:
            print(f"✓ 字段存在: {field}")
    
    # 检查节点
    nodes = workflow.get('nodes', [])
    print(f"\n✓ 节点数量: {len(nodes)}")
    
    for node in nodes:
        node_id = node.get('id', 'unknown')
        node_type = node.get('type', 'unknown')
        node_title = node.get('title', node_type)
        
        # 检查节点必需字段
        if 'id' not in node:
            print(f"  ❌ 节点缺少 id")
            return False
        if 'type' not in node:
            print(f"  ❌ 节点 {node_id} 缺少 type")
            return False
        if 'pos' not in node:
            print(f"  ⚠ 节点 {node_id} ({node_type}) 缺少 pos")
        if 'widgets_values' not in node:
            print(f"  ⚠ 节点 {node_id} ({node_type}) 缺少 widgets_values")
        
        print(f"  ✓ 节点 {node_id}: {node_type} ({node_title})")
    
    # 检查连接
    links = workflow.get('links', [])
    print(f"\n✓ 连接数量: {len(links)}")
    
    for link in links:
        if len(link) < 5:
            print(f"  ❌ 连接格式错误: {link}")
            return False
        
        link_id, from_node, from_slot, to_node, to_slot, link_type = link[:6]
        print(f"  ✓ 连接 {link_id}: 节点{from_node}[{from_slot}] -> 节点{to_node}[{to_slot}] ({link_type})")
    
    # 检查节点 ID 连续性
    node_ids = [n['id'] for n in nodes]
    max_id = max(node_ids)
    if workflow['last_node_id'] < max_id:
        print(f"\n⚠ last_node_id ({workflow['last_node_id']}) 小于最大节点 ID ({max_id})")
    
    # 检查连接 ID 连续性
    link_ids = [l[0] for l in links]
    max_link_id = max(link_ids) if link_ids else 0
    if workflow['last_link_id'] < max_link_id:
        print(f"⚠ last_link_id ({workflow['last_link_id']}) 小于最大连接 ID ({max_link_id})")
    
    print("\n" + "=" * 60)
    print("✅ 工作流格式验证通过！")
    print("=" * 60)
    
    return True


def main():
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        filepath = "novel_to_drama_complete.json"
    
    success = validate_comfyui_workflow(filepath)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
