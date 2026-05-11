#!/usr/bin/env python3
"""
ComfyUI-UnlimitAI 全面检测脚本

检测内容：
1. Python语法检查
2. 节点注册验证
3. 导入依赖检查
4. 文件完整性验证
5. 配置文件验证
6. 文档链接检查
"""

import sys
import json
import ast
import importlib.util
from pathlib import Path
from typing import List, Dict, Tuple


class ProjectChecker:
    """项目检查器"""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.errors = []
        self.warnings = []
        self.info = []
    
    def check_all(self) -> bool:
        """运行所有检查"""
        print("="*60)
        print("ComfyUI-UnlimitAI 项目检测")
        print("="*60)
        
        # 1. 文件结构检查
        self.check_file_structure()
        
        # 2. Python语法检查
        self.check_python_syntax()
        
        # 3. 节点注册检查
        self.check_node_registration()
        
        # 4. 导入依赖检查
        self.check_imports()
        
        # 5. 配置文件检查
        self.check_config_files()
        
        # 6. 文档检查
        self.check_documentation()
        
        # 输出结果
        self.print_results()
        
        return len(self.errors) == 0
    
    def check_file_structure(self):
        """检查文件结构"""
        print("\n📁 检查文件结构...")
        
        required_files = [
            "__init__.py",
            "nodes/text_nodes.py",
            "nodes/image_nodes.py",
            "nodes/video_nodes.py",
            "nodes/audio_nodes.py",
            "nodes/music_nodes.py",
            "nodes/workflow_nodes.py",
            "nodes/config_nodes.py",
            "nodes/optimized_nodes.py",
            "nodes/advanced_nodes.py",
            "nodes/character_nodes.py",
        ]
        
        for file_path in required_files:
            full_path = self.base_path / file_path
            if not full_path.exists():
                self.errors.append(f"缺少文件: {file_path}")
            else:
                self.info.append(f"✅ 找到文件: {file_path}")
    
    def check_python_syntax(self):
        """检查Python语法"""
        print("\n🔍 检查Python语法...")
        
        python_files = list(self.base_path.glob("**/*.py"))
        
        for py_file in python_files:
            if "__pycache__" in str(py_file):
                continue
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    code = f.read()
                
                # 尝试解析AST
                ast.parse(code)
                self.info.append(f"✅ 语法正确: {py_file.relative_to(self.base_path)}")
                
            except SyntaxError as e:
                self.errors.append(f"语法错误 {py_file.name}: {e}")
            except Exception as e:
                self.warnings.append(f"读取失败 {py_file.name}: {e}")
    
    def check_node_registration(self):
        """检查节点注册"""
        print("\n📝 检查节点注册...")
        
        try:
            # 检查__init__.py
            init_file = self.base_path / "__init__.py"
            with open(init_file, 'r', encoding='utf-8') as f:
                init_content = f.read()
            
            # 检查必要的映射
            required_mappings = [
                "NODE_CLASS_MAPPINGS",
                "NODE_DISPLAY_NAME_MAPPINGS"
            ]
            
            for mapping in required_mappings:
                if mapping not in init_content:
                    self.errors.append(f"__init__.py 缺少 {mapping}")
                else:
                    self.info.append(f"✅ 找到 {mapping}")
            
            # 检查节点导入
            node_files = [
                "text_nodes",
                "image_nodes",
                "video_nodes",
                "audio_nodes",
                "music_nodes",
                "workflow_nodes",
                "config_nodes",
                "optimized_nodes",
                "advanced_nodes",
                "character_nodes"
            ]
            
            for node_file in node_files:
                if node_file not in init_content:
                    self.errors.append(f"__init__.py 未导入 {node_file}")
                else:
                    self.info.append(f"✅ 已导入 {node_file}")
            
        except Exception as e:
            self.errors.append(f"节点注册检查失败: {e}")
    
    def check_imports(self):
        """检查导入依赖"""
        print("\n📦 检查导入依赖...")
        
        # 检查节点文件
        node_files = list((self.base_path / "nodes").glob("*.py"))
        
        for node_file in node_files:
            try:
                with open(node_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检查是否有NODE_CLASS_MAPPINGS
                if "NODE_CLASS_MAPPINGS" not in content:
                    self.warnings.append(f"{node_file.name} 未定义 NODE_CLASS_MAPPINGS")
                else:
                    self.info.append(f"✅ {node_file.name} 定义了节点映射")
                
                # 检查是否有NODE_DISPLAY_NAME_MAPPINGS
                if "NODE_DISPLAY_NAME_MAPPINGS" not in content:
                    self.warnings.append(f"{node_file.name} 未定义 NODE_DISPLAY_NAME_MAPPINGS")
                
            except Exception as e:
                self.warnings.append(f"检查 {node_file.name} 导入失败: {e}")
    
    def check_config_files(self):
        """检查配置文件"""
        print("\n⚙️ 检查配置文件...")
        
        config_dir = self.base_path / "workflow_configs"
        
        if not config_dir.exists():
            self.errors.append("缺少 workflow_configs 目录")
            return
        
        config_files = [
            "budget_config.json",
            "balanced_config.json",
            "quality_config.json",
            "max_quality_config.json"
        ]
        
        for config_file in config_files:
            config_path = config_dir / config_file
            
            if not config_path.exists():
                self.errors.append(f"缺少配置文件: {config_file}")
                continue
            
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # 检查必要字段
                required_fields = ["name", "models", "cost_breakdown"]
                for field in required_fields:
                    if field not in config:
                        self.warnings.append(f"{config_file} 缺少字段: {field}")
                
                self.info.append(f"✅ 配置有效: {config_file}")
                
            except json.JSONDecodeError as e:
                self.errors.append(f"{config_file} JSON格式错误: {e}")
            except Exception as e:
                self.warnings.append(f"读取 {config_file} 失败: {e}")
    
    def check_documentation(self):
        """检查文档"""
        print("\n📚 检查文档...")
        
        required_docs = [
            "README.md",
            "PROGRESS.md",
            "OPTIMIZATION_STRATEGIES.md",
            "OPTIMIZATION_SUMMARY.md",
            "ADVANCED_FEATURES_GUIDE.md",
            "CHARACTER_MANAGEMENT_GUIDE.md"
        ]
        
        for doc in required_docs:
            doc_path = self.base_path / doc
            
            if not doc_path.exists():
                self.warnings.append(f"缺少文档: {doc}")
            else:
                # 检查文档大小
                size = doc_path.stat().st_size
                if size < 100:
                    self.warnings.append(f"文档过小: {doc} ({size} bytes)")
                else:
                    self.info.append(f"✅ 文档存在: {doc} ({size} bytes)")
    
    def print_results(self):
        """输出检查结果"""
        print("\n" + "="*60)
        print("检测结果")
        print("="*60)
        
        # 错误
        if self.errors:
            print(f"\n❌ 错误 ({len(self.errors)}):")
            for error in self.errors:
                print(f"  - {error}")
        
        # 警告
        if self.warnings:
            print(f"\n⚠️ 警告 ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  - {warning}")
        
        # 信息
        print(f"\n✅ 通过项 ({len(self.info)}):")
        for info in self.info[:20]:  # 只显示前20项
            print(f"  {info}")
        
        if len(self.info) > 20:
            print(f"  ... 还有 {len(self.info) - 20} 项")
        
        # 总结
        print("\n" + "="*60)
        if len(self.errors) == 0:
            print("✅ 项目检测通过")
            print(f"   通过项: {len(self.info)}")
            print(f"   警告项: {len(self.warnings)}")
        else:
            print("❌ 项目检测失败")
            print(f"   错误项: {len(self.errors)}")
            print(f"   警告项: {len(self.warnings)}")
        print("="*60)


def check_node_definitions(base_path: Path) -> Dict:
    """检查节点定义"""
    print("\n🔍 检查节点定义...")
    
    node_counts = {}
    
    node_files = {
        "text_nodes.py": "文本节点",
        "image_nodes.py": "图像节点",
        "video_nodes.py": "视频节点",
        "audio_nodes.py": "音频节点",
        "music_nodes.py": "音乐节点",
        "workflow_nodes.py": "工作流节点",
        "config_nodes.py": "配置节点",
        "optimized_nodes.py": "优化节点",
        "advanced_nodes.py": "高级节点",
        "character_nodes.py": "角色节点"
    }
    
    for file_name, category in node_files.items():
        file_path = base_path / "nodes" / file_name
        
        if not file_path.exists():
            print(f"  ❌ 文件不存在: {file_name}")
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 统计节点类数量
            import re
            node_classes = re.findall(r'class (\w+Node)', content)
            count = len(node_classes)
            
            node_counts[category] = {
                "count": count,
                "nodes": node_classes,
                "file": file_name
            }
            
            print(f"  ✅ {category}: {count}个")
            for node in node_classes:
                print(f"     - {node}")
            
        except Exception as e:
            print(f"  ❌ 读取 {file_name} 失败: {e}")
    
    # 统计总数
    total = sum(item["count"] for item in node_counts.values())
    print(f"\n📊 节点总数: {total}个")
    
    return node_counts


def check_data_types(base_path: Path) -> None:
    """检查数据类型定义"""
    print("\n🔍 检查数据类型...")
    
    custom_types = [
        "CHARACTER",
        "VOICE",
        "CHARACTER_PROFILE"
    ]
    
    character_nodes = base_path / "nodes" / "character_nodes.py"
    
    if not character_nodes.exists():
        print("  ❌ character_nodes.py 不存在")
        return
    
    try:
        with open(character_nodes, 'r', encoding='utf-8') as f:
            content = f.read()
        
        for dtype in custom_types:
            if dtype in content:
                print(f"  ✅ 定义了数据类型: {dtype}")
            else:
                print(f"  ⚠️ 未找到数据类型: {dtype}")
        
    except Exception as e:
        print(f"  ❌ 检查数据类型失败: {e}")


def main():
    """主函数"""
    base_path = Path(__file__).parent
    
    # 1. 基础检查
    checker = ProjectChecker(base_path)
    success = checker.check_all()
    
    # 2. 节点定义检查
    node_counts = check_node_definitions(base_path)
    
    # 3. 数据类型检查
    check_data_types(base_path)
    
    # 返回状态码
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
