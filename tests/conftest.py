"""
测试配置和共享fixtures

提供：
- 测试数据和fixtures
- Mock对象
- 测试工具函数
"""

import pytest
import os
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock
from typing import Dict, Any

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


# ============================================================================
# 配置
# ============================================================================

def pytest_configure(config):
    """Pytest配置"""
    config.addinivalue_line(
        "markers", "unit: Unit tests (fast, no external dependencies)"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests (may require external services)"
    )
    config.addinivalue_line(
        "markers", "slow: Slow running tests"
    )
    config.addinivalue_line(
        "markers", "api: Tests that require API access"
    )


def pytest_collection_modifyitems(config, items):
    """根据标记修改测试收集"""
    # 如果指定了标记，只运行对应的测试
    markers = config.getoption("-m")
    if not markers:
        # 默认跳过慢速测试和API测试
        skip_slow = pytest.mark.skip(reason="需要指定 -m slow 来运行慢速测试")
        skip_api = pytest.mark.skip(reason="需要指定 -m api 来运行API测试")
        
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_slow)
            if "api" in item.keywords:
                item.add_marker(skip_api)


# ============================================================================
# Fixtures - 测试数据
# ============================================================================

@pytest.fixture
def sample_text():
    """示例文本"""
    return "这是一个测试文本，用于测试文本处理功能。"


@pytest.fixture
def sample_prompt():
    """示例提示词"""
    return "一个穿着蓝色裙子的女孩站在樱花树下，微风拂过，花瓣飘落"


@pytest.fixture
def sample_character_data():
    """示例角色数据"""
    return {
        "name": "小明",
        "age": 18,
        "gender": "male",
        "appearance": "短发，圆脸，戴眼镜",
        "personality": "开朗，乐观",
        "description": "一个普通的高中生，热爱篮球"
    }


@pytest.fixture
def sample_scene_data():
    """示例场景数据"""
    return {
        "scene_id": "scene_001",
        "location": "学校操场",
        "time": "下午",
        "weather": "晴天",
        "characters": ["小明", "小红"],
        "action": "打篮球",
        "dialogue": [
            {"speaker": "小明", "text": "传球给我！"},
            {"speaker": "小红", "text": "接好！"}
        ]
    }


@pytest.fixture
def sample_novel_content():
    """示例小说内容"""
    return """
    第一章 开始
    
    阳光明媚的下午，小明站在学校操场上。
    
    "传球给我！"他大声喊道。
    
    小红接到球，用力扔了回去。"接好！"
    
    篮球在空中划出一道优美的弧线。
    """


@pytest.fixture
def sample_api_response():
    """示例API响应"""
    return {
        "success": True,
        "data": {
            "text": "生成的文本内容",
            "model": "deepseek-chat",
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 200,
                "total_tokens": 300
            }
        }
    }


@pytest.fixture
def sample_image_response():
    """示例图像API响应"""
    return {
        "success": True,
        "data": {
            "images": [
                {
                    "url": "https://example.com/image1.png",
                    "seed": 12345
                }
            ],
            "model": "flux.1-schnell",
            "timing": {
                "inference": 2.5
            }
        }
    }


@pytest.fixture
def sample_video_response():
    """示例视频API响应"""
    return {
        "success": True,
        "data": {
            "videos": [
                {
                    "url": "https://example.com/video1.mp4",
                    "duration": 5.0
                }
            ],
            "model": "kling-video-v2",
            "timing": {
                "inference": 120.5
            }
        }
    }


# ============================================================================
# Fixtures - Mock对象
# ============================================================================

@pytest.fixture
def mock_api_client():
    """Mock API客户端"""
    from utils.api_client import UnlimitAIClient
    
    client = Mock(spec=UnlimitAIClient)
    client.generate_text = Mock(return_value="生成的文本")
    client.generate_image = Mock(return_value="https://example.com/image.png")
    client.generate_video = Mock(return_value="https://example.com/video.mp4")
    client.generate_audio = Mock(return_value="https://example.com/audio.wav")
    client.generate_music = Mock(return_value="https://example.com/music.mp3")
    
    return client


@pytest.fixture
def mock_logger():
    """Mock日志器"""
    from unittest.mock import Mock
    
    logger = Mock()
    logger.debug = Mock()
    logger.info = Mock()
    logger.warning = Mock()
    logger.error = Mock()
    logger.critical = Mock()
    
    return logger


@pytest.fixture
def mock_config():
    """Mock配置"""
    return {
        "api_key": "test_api_key_12345",
        "api_base_url": "https://api.unlimitai.org",
        "default_model": {
            "text": "deepseek-chat",
            "image": "flux.1-schnell",
            "video": "kling-video-v2",
            "audio": "tts-1",
            "music": "musicgen"
        },
        "generation": {
            "max_retries": 3,
            "timeout": 60,
            "default_image_size": "1024x1024",
            "default_video_duration": 5.0
        }
    }


@pytest.fixture
def mock_environment(monkeypatch):
    """Mock环境变量"""
    monkeypatch.setenv("UNITED_API_KEY", "test_api_key")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    yield


# ============================================================================
# Fixtures - 临时文件
# ============================================================================

@pytest.fixture
def temp_dir(tmp_path):
    """临时目录"""
    test_dir = tmp_path / "test_data"
    test_dir.mkdir(exist_ok=True)
    return test_dir


@pytest.fixture
def temp_json_file(temp_dir):
    """临时JSON文件"""
    import json
    
    json_file = temp_dir / "test_data.json"
    test_data = {
        "name": "test",
        "value": 123
    }
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(test_data, f)
    
    yield json_file
    
    # 清理
    if json_file.exists():
        json_file.unlink()


# ============================================================================
# Fixtures - 数据库
# ============================================================================

@pytest.fixture
def temp_database(temp_dir):
    """临时数据库"""
    from utils.persistent_storage import CharacterDatabase
    
    db_path = temp_dir / "test_characters.json"
    db = CharacterDatabase(str(db_path))
    
    yield db
    
    # 清理
    if db_path.exists():
        db_path.unlink()


# ============================================================================
# 工具函数
# ============================================================================

def create_test_image(width: int = 512, height: int = 512):
    """创建测试图像"""
    from PIL import Image
    import numpy as np
    
    # 创建随机图像
    arr = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
    image = Image.fromarray(arr)
    
    return image


def create_test_audio(duration: float = 1.0, sample_rate: int = 22050):
    """创建测试音频"""
    import numpy as np
    
    # 创建正弦波
    t = np.linspace(0, duration, int(sample_rate * duration))
    frequency = 440  # A4音符
    audio = np.sin(2 * np.pi * frequency * t)
    
    return audio, sample_rate


def assert_valid_url(url: str):
    """验证URL格式"""
    from urllib.parse import urlparse
    
    result = urlparse(url)
    assert result.scheme in ['http', 'https']
    assert result.netloc


def assert_file_exists(path: str):
    """验证文件存在"""
    from pathlib import Path
    
    file_path = Path(path)
    assert file_path.exists(), f"文件不存在: {path}"
    assert file_path.is_file(), f"不是文件: {path}"


# ============================================================================
# Parametrize数据
# ============================================================================

@pytest.fixture(params=[
    ("flux.1-schnell", "image"),
    ("kling-video-v2", "video"),
    ("deepseek-chat", "text"),
    ("tts-1", "audio"),
    ("musicgen", "music")
])
def model_type_pair(request):
    """模型-类型对"""
    return request.param


@pytest.fixture(params=[
    ("budget", {"quality": "low", "cost": "low"}),
    ("balanced", {"quality": "medium", "cost": "medium"}),
    ("quality", {"quality": "high", "cost": "high"}),
    ("max_quality", {"quality": "very_high", "cost": "very_high"})
])
def workflow_config(request):
    """工作流配置"""
    return request.param


# ============================================================================
# Skip标记
# ============================================================================

def pytest_addoption(parser):
    """添加命令行选项"""
    parser.addoption(
        "--run-slow",
        action="store_true",
        default=False,
        help="运行慢速测试"
    )
    parser.addoption(
        "--run-api",
        action="store_true",
        default=False,
        help="运行API测试"
    )
    parser.addoption(
        "--run-integration",
        action="store_true",
        default=False,
        help="运行集成测试"
    )


def pytest_runtest_setup(item):
    """测试运行前设置"""
    # 检查是否需要跳过慢速测试
    if "slow" in item.keywords and not item.config.getoption("--run-slow"):
        pytest.skip("需要 --run-slow 选项来运行慢速测试")
    
    # 检查是否需要跳过API测试
    if "api" in item.keywords and not item.config.getoption("--run-api"):
        pytest.skip("需要 --run-api 选项来运行API测试")
    
    # 检查是否需要跳过集成测试
    if "integration" in item.keywords and not item.config.getoption("--run-integration"):
        pytest.skip("需要 --run-integration 选项来运行集成测试")
