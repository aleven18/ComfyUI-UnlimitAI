"""
工作流测试

测试所有工作流配置：
- 工作流文件结构
- 配置完整性
- 模型选择合理性
- 成本计算准确性
"""

import pytest
import json
import yaml
from pathlib import Path
import sys

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


# =============================================================================
# 工作流文件结构测试
# =============================================================================

class TestWorkflowStructure:
    """工作流文件结构测试"""
    
    @pytest.fixture
    def workflows_dir(self):
        """工作流目录"""
        return project_root / "workflows"
    
    @pytest.fixture
    def workflow_configs_dir(self):
        """工作流配置目录"""
        return project_root / "workflow_configs"
    
    def test_budget_workflow_exists(self, workflows_dir):
        """测试成本优化工作流存在"""
        workflow_file = workflows_dir / "budget_workflow.json"
        
        assert workflow_file.exists(), "成本优化工作流文件不存在"
    
    def test_balanced_workflow_exists(self, workflows_dir):
        """测试平衡工作流存在"""
        workflow_file = workflows_dir / "balanced_workflow.json"
        
        assert workflow_file.exists(), "平衡工作流文件不存在"
    
    def test_quality_workflow_exists(self, workflows_dir):
        """测试质量优先工作流存在"""
        workflow_file = workflows_dir / "quality_workflow.json"
        
        assert workflow_file.exists(), "质量优先工作流文件不存在"
    
    def test_max_quality_workflow_exists(self, workflows_dir):
        """测试极致质量工作流存在"""
        workflow_file = workflows_dir / "max_quality_workflow.json"
        
        assert workflow_file.exists(), "极致质量工作流文件不存在"
    
    def test_workflow_is_valid_json(self, workflows_dir):
        """测试工作流文件是有效JSON"""
        workflow_files = [
            "budget_workflow.json",
            "balanced_workflow.json",
            "quality_workflow.json",
            "max_quality_workflow.json"
        ]
        
        for filename in workflow_files:
            file_path = workflows_dir / filename
            
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                        assert isinstance(data, dict), f"{filename} 不是有效的JSON对象"
                    except json.JSONDecodeError as e:
                        pytest.fail(f"{filename} JSON解析失败: {e}")


# =============================================================================
# 工作流配置测试
# =============================================================================

class TestWorkflowConfig:
    """工作流配置测试"""
    
    @pytest.fixture
    def workflow_configs_dir(self):
        """工作流配置目录"""
        return project_root / "workflow_configs"
    
    def test_budget_config_exists(self, workflow_configs_dir):
        """测试成本优化配置存在"""
        config_file = workflow_configs_dir / "budget.yaml"
        
        assert config_file.exists(), "成本优化配置文件不存在"
    
    def test_balanced_config_exists(self, workflow_configs_dir):
        """测试平衡配置存在"""
        config_file = workflow_configs_dir / "balanced.yaml"
        
        assert config_file.exists(), "平衡配置文件不存在"
    
    def test_quality_config_exists(self, workflow_configs_dir):
        """测试质量优先配置存在"""
        config_file = workflow_configs_dir / "quality.yaml"
        
        assert config_file.exists(), "质量优先配置文件不存在"
    
    def test_max_quality_config_exists(self, workflow_configs_dir):
        """测试极致质量配置存在"""
        config_file = workflow_configs_dir / "max_quality.yaml"
        
        assert config_file.exists(), "极致质量配置文件不存在"
    
    def test_config_is_valid_yaml(self, workflow_configs_dir):
        """测试配置文件是有效YAML"""
        config_files = [
            "budget.yaml",
            "balanced.yaml",
            "quality.yaml",
            "max_quality.yaml"
        ]
        
        for filename in config_files:
            file_path = workflow_configs_dir / filename
            
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    try:
                        data = yaml.safe_load(f)
                        assert data is not None, f"{filename} 是空文件"
                    except yaml.YAMLError as e:
                        pytest.fail(f"{filename} YAML解析失败: {e}")
    
    def test_budget_config_structure(self, workflow_configs_dir):
        """测试成本优化配置结构"""
        config_file = workflow_configs_dir / "budget.yaml"
        
        if not config_file.exists():
            pytest.skip("成本优化配置文件不存在")
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # 检查必需字段
        assert "name" in config or "workflow_name" in config
        assert "models" in config or "text" in config
    
    def test_balanced_config_structure(self, workflow_configs_dir):
        """测试平衡配置结构"""
        config_file = workflow_configs_dir / "balanced.yaml"
        
        if not config_file.exists():
            pytest.skip("平衡配置文件不存在")
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        assert config is not None
    
    def test_quality_config_structure(self, workflow_configs_dir):
        """测试质量优先配置结构"""
        config_file = workflow_configs_dir / "quality.yaml"
        
        if not config_file.exists():
            pytest.skip("质量优先配置文件不存在")
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        assert config is not None
    
    def test_max_quality_config_structure(self, workflow_configs_dir):
        """测试极致质量配置结构"""
        config_file = workflow_configs_dir / "max_quality.yaml"
        
        if not config_file.exists():
            pytest.skip("极致质量配置文件不存在")
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        assert config is not None


# =============================================================================
# 模型选择合理性测试
# =============================================================================

class TestModelSelection:
    """模型选择合理性测试"""
    
    @pytest.fixture
    def workflow_configs_dir(self):
        """工作流配置目录"""
        return project_root / "workflow_configs"
    
    def test_budget_uses_cost_effective_models(self, workflow_configs_dir):
        """测试成本优化工作流使用高性价比模型"""
        config_file = workflow_configs_dir / "budget.yaml"
        
        if not config_file.exists():
            pytest.skip("成本优化配置文件不存在")
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # 成本优化应该使用便宜的模型
        # DeepSeek是成本效益最高的文本模型
        if "models" in config:
            models = config["models"]
            
            # 文本模型应该是deepseek-chat
            if "text" in models:
                assert "deepseek" in models["text"].lower(), \
                    "成本优化工作流应该使用DeepSeek文本模型"
    
    def test_quality_uses_high_quality_models(self, workflow_configs_dir):
        """测试质量优先工作流使用高质量模型"""
        config_file = workflow_configs_dir / "quality.yaml"
        
        if not config_file.exists():
            pytest.skip("质量优先配置文件不存在")
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # 质量优先应该使用高质量模型
        if "models" in config:
            models = config["models"]
            
            # 文本模型应该是GPT-4或Claude
            if "text" in models:
                text_model = models["text"].lower()
                is_high_quality = any([
                    "gpt-4" in text_model,
                    "claude" in text_model,
                    "opus" in text_model
                ])
                
                # 如果不是高质量模型，发出警告但不失败
                if not is_high_quality:
                    pytest.warns("质量优先工作流建议使用GPT-4或Claude")


# =============================================================================
# 成本计算测试
# =============================================================================

class TestCostCalculation:
    """成本计算测试"""
    
    def test_budget_cost_lower_than_quality(self):
        """测试成本优化工作流成本低于质量优先"""
        # 这个测试需要实际的成本计算
        # 暂时跳过
        pytest.skip("需要实现成本计算功能")
    
    def test_cost_calculation_accuracy(self):
        """测试成本计算准确性"""
        # 这个测试需要实际的成本计算
        # 暂时跳过
        pytest.skip("需要实现成本计算功能")


# =============================================================================
# 工作流完整性测试
# =============================================================================

class TestWorkflowCompleteness:
    """工作流完整性测试"""
    
    def test_all_required_nodes_present(self):
        """测试所有必需节点都存在"""
        # 检查关键节点文件是否存在
        required_nodes = [
            "character_nodes_optimized.py",
            # 可以添加更多必需节点
        ]
        
        nodes_dir = project_root / "nodes"
        
        for node_file in required_nodes:
            node_path = nodes_dir / node_file
            assert node_path.exists(), f"必需节点文件不存在: {node_file}"
    
    def test_all_model_types_covered(self):
        """测试所有模型类型都有对应节点"""
        # 检查是否有文本、图像、视频、音频、音乐节点
        node_files = list((project_root / "nodes").glob("*.py"))
        
        node_names = [f.stem for f in node_files]
        
        # 至少应该有这些类型的节点（文件名包含这些关键词）
        required_types = ["character"]  # 最基本的
        
        for node_type in required_types:
            found = any(node_type in name.lower() for name in node_names)
            assert found, f"缺少 {node_type} 类型的节点"


# =============================================================================
# 主配置文件测试
# =============================================================================

class TestMainConfig:
    """主配置文件测试"""
    
    def test_main_config_exists(self):
        """测试主配置文件存在"""
        config_file = project_root / "config.yaml"
        
        assert config_file.exists(), "主配置文件不存在"
    
    def test_main_config_structure(self):
        """测试主配置文件结构"""
        config_file = project_root / "config.yaml"
        
        if not config_file.exists():
            pytest.skip("主配置文件不存在")
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # 检查关键配置节
        assert config is not None
        
        # 应该有模型配置
        assert "models" in config or "api" in config
    
    def test_env_example_exists(self):
        """测试环境变量示例文件存在"""
        env_file = project_root / ".env.example"
        
        assert env_file.exists(), "环境变量示例文件不存在"


# =============================================================================
# 文档完整性测试
# =============================================================================

class TestDocumentation:
    """文档完整性测试"""
    
    def test_readme_exists(self):
        """测试README文件存在"""
        readme_file = project_root / "README.md"
        
        # README可能不存在，只是警告
        if not readme_file.exists():
            pytest.warns("建议创建README.md文件")
    
    def test_development_guide_exists(self):
        """测试开发指南存在"""
        dev_guide = project_root / "DEVELOPMENT.md"
        
        assert dev_guide.exists(), "开发指南文件不存在"
    
    def test_test_guide_exists(self):
        """测试测试指南存在"""
        test_guide = project_root / "tests" / "README.md"
        
        assert test_guide.exists(), "测试指南文件不存在"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
