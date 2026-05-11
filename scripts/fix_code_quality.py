#!/usr/bin/env python3
"""
代码质量快速修复脚本

自动修复代码质量问题：
1. 为节点文件添加日志导入
2. 统一代码风格
"""

import re
from pathlib import Path

def add_logging_import(file_path):
    """为Python文件添加日志导入"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已有logging导入
    if 'import logging' in content or 'from utils.logger' in content:
        print(f"✓ {file_path.name} 已有日志导入")
        return False
    
    # 找到第一个import语句的位置
    lines = content.split('\n')
    insert_pos = 0
    
    for i, line in enumerate(lines):
        if line.startswith('import ') or line.startswith('from '):
            insert_pos = i
            break
    
    # 插入logging导入
    logging_import = 'import logging\nlogger = logging.getLogger(__name__)\n'
    lines.insert(insert_pos, logging_import)
    
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"✓ 已为 {file_path.name} 添加日志导入")
    return True

def main():
    """主函数"""
    nodes_dir = Path(__file__).parent.parent / 'nodes'
    
    print("=" * 60)
    print("代码质量快速修复")
    print("=" * 60)
    
    # 需要添加日志的文件
    files_to_fix = [
        'text_nodes.py',
        'video_nodes.py',
        'music_nodes.py',
        'workflow_nodes.py',
        'optimized_nodes.py',
        'config_nodes.py',
        'audio_nodes.py',
        'advanced_nodes.py',
        'character_nodes.py'
    ]
    
    fixed_count = 0
    
    for filename in files_to_fix:
        file_path = nodes_dir / filename
        
        if file_path.exists():
            if add_logging_import(file_path):
                fixed_count += 1
    
    print("\n" + "=" * 60)
    print(f"✅ 完成！共修复 {fixed_count} 个文件")
    print("=" * 60)

if __name__ == '__main__':
    main()
