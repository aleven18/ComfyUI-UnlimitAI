# 开发指南

## 项目概述

**ComfyUI-UnlimitAI** 是一个基于 ComfyUI 的插件，用于将小说转换为动态漫剧。通过 UnlimitAI API，实现文本、图像、视频、音频、音乐的自动化生成。

### 核心功能

- 📝 **文本生成**：小说分析、场景提取、对话生成
- 🎨 **图像生成**：角色立绘、场景插画、分镜图
- 🎬 **视频生成**：场景动画、角色动作、过渡效果
- 🎙️ **音频生成**：语音合成、音效生成
- 🎵 **音乐生成**：背景音乐、氛围音
- 👥 **角色管理**：角色一致性维护
- 💰 **成本优化**：智能选择模型，节省30-61%成本

### 技术栈

- **语言**: Python 3.8+
- **框架**: ComfyUI
- **API**: UnlimitAI
- **数据库**: JSON文件
- **测试**: pytest
- **类型检查**: mypy
- **代码风格**: black, isort

---

## 安装指南

### 1. 环境要求

- Python 3.8 或更高版本
- ComfyUI 已安装
- UnlimitAI API Key

### 2. 安装步骤

```bash
# 克隆仓库
git clone https://github.com/your-repo/ComfyUI-UnlimitAI.git
cd ComfyUI-UnlimitAI

# 安装依赖
pip install -r requirements.txt

# 安装开发依赖（可选）
pip install -r requirements-dev.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填写 API Key

# 运行测试
python run_tests.py
```

### 3. 在 ComfyUI 中使用

```bash
# 将项目链接到 ComfyUI custom_nodes 目录
ln -s $(pwd) /path/to/ComfyUI/custom_nodes/ComfyUI-UnlimitAI
```

---

## 开发环境配置

### IDE 配置

#### VS Code

创建 `.vscode/settings.json`：

```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": ["--line-length=100"],
  "editor.formatOnSave": true,
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests"]
}
```

#### PyCharm

1. 设置 Python 解释器
2. 启用 pytest 测试框架
3. 配置 black 格式化器
4. 启用 mypy 类型检查

### 环境变量

在 `.env` 文件中配置：

```bash
# 必需
UNITED_API_KEY=your_api_key_here

# 可选
LOG_LEVEL=INFO
DEFAULT_TEXT_MODEL=deepseek-chat
DEFAULT_IMAGE_MODEL=flux.1-schnell
```

---

## 项目结构

```
ComfyUI-UnlimitAI/
├── nodes/                      # ComfyUI节点
│   ├── text_nodes.py          # 文本生成节点
│   ├── image_nodes.py         # 图像生成节点
│   ├── video_nodes.py         # 视频生成节点
│   ├── audio_nodes.py         # 音频生成节点
│   ├── music_nodes.py         # 音乐生成节点
│   ├── character_nodes_optimized.py  # 角色管理节点
│   └── ...
├── utils/                      # 工具模块
│   ├── api_client.py          # API客户端
│   ├── config.py              # 配置管理
│   ├── logger.py              # 日志系统
│   ├── exceptions.py          # 异常处理
│   ├── delay.py               # 智能延迟
│   ├── types.py               # 类型定义
│   └── persistent_storage.py  # 持久化存储
├── tests/                      # 测试文件
│   ├── conftest.py            # 测试配置
│   ├── test_api_client.py     # API测试
│   ├── test_character_nodes.py # 角色节点测试
│   └── ...
├── workflows/                  # 工作流配置
│   ├── budget_workflow.json
│   ├── balanced_workflow.json
│   ├── quality_workflow.json
│   └── max_quality_workflow.json
├── workflow_configs/           # 工作流参数配置
│   ├── budget.yaml
│   ├── balanced.yaml
│   ├── quality.yaml
│   └── max_quality.yaml
├── requirements.txt            # 生产依赖
├── requirements-dev.txt        # 开发依赖
├── config.yaml                 # 配置文件
├── .env.example                # 环境变量模板
├── pytest.ini                 # pytest配置
├── mypy.ini                   # mypy配置
├── run_tests.py               # 测试运行脚本
└── README.md                  # 项目说明
```

---

## 代码规范

### 1. 命名规范

```python
# 模块名：小写下划线
# my_module.py

# 类名：大驼峰
class CharacterManager:
    pass

# 函数名：小写下划线
def generate_image():
    pass

# 变量名：小写下划线
character_data = {}

# 常量：大写下划线
MAX_RETRIES = 3

# 私有方法：前缀下划线
def _internal_method():
    pass
```

### 2. 类型注解

```python
from typing import Dict, List, Optional
from utils.types import CharacterData

def create_character(
    name: str,
    age: int,
    gender: str = "male"
) -> CharacterData:
    """创建角色"""
    return {
        "name": name,
        "age": age,
        "gender": gender
    }
```

### 3. 文档字符串

```python
def generate_video(
    prompt: str,
    model: str = "kling-video-v2",
    duration: float = 5.0
) -> str:
    """
    生成视频
    
    Args:
        prompt: 视频描述提示词
        model: 视频生成模型名称
        duration: 视频时长（秒）
    
    Returns:
        生成的视频URL
    
    Raises:
        ValidationError: 参数验证失败
        APIError: API调用失败
    
    Examples:
        >>> url = generate_video("一个女孩在跳舞", duration=10.0)
        >>> print(url)
        'https://example.com/video.mp4'
    """
    pass
```

### 4. 异常处理

```python
from utils.exceptions import ValidationError, APIError
from utils.logger import get_logger

logger = get_logger(__name__)

def risky_operation():
    """执行可能失败的操作"""
    try:
        result = some_operation()
        logger.info("操作成功")
        return result
    except ValidationError as e:
        logger.error(f"验证失败: {e}")
        raise
    except APIError as e:
        logger.error(f"API错误: {e}")
        raise
    except Exception as e:
        logger.error(f"未知错误: {e}", exc_info=True)
        raise
```

### 5. 日志使用

```python
from utils.logger import get_logger

logger = get_logger(__name__)

# 不同级别日志
logger.debug("调试信息")
logger.info("普通信息")
logger.warning("警告信息")
logger.error("错误信息", exc_info=True)
logger.critical("严重错误")

# 带额外数据
logger.info("用户登录", extra={"data": {"user_id": 123}})
```

---

## 测试指南

### 运行测试

```bash
# 运行所有单元测试
pytest tests/

# 运行特定测试文件
pytest tests/test_api_client.py

# 运行带覆盖率的测试
pytest tests/ --cov=. --cov-report=html

# 运行慢速测试
pytest tests/ --run-slow

# 运行API测试
pytest tests/ --run-api
```

### 编写测试

```python
import pytest
from utils.api_client import UnlimitAIClient

class TestUnlimitAIClient:
    """API客户端测试"""
    
    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        return UnlimitAIClient(api_key="test_key")
    
    def test_generate_text_success(self, client):
        """测试文本生成成功"""
        result = client.generate_text(
            prompt="测试",
            model="deepseek-chat"
        )
        assert result is not None
```

---

## 性能优化

### 1. 使用缓存

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_computation(data):
    """昂贵的计算操作"""
    return result
```

### 2. 异步操作

```python
import asyncio
from utils.delay import delay_async

async def batch_generate(prompts):
    """批量生成"""
    tasks = [generate_async(p) for p in prompts]
    results = await asyncio.gather(*tasks)
    return results
```

### 3. 智能延迟

```python
from utils.delay import SmartDelay

delay = SmartDelay()

for prompt in prompts:
    delay.wait("api_call")
    result = api.generate(prompt)
    delay.on_success()
```

---

## 调试技巧

### 1. 使用调试器

```python
import pdb; pdb.set_trace()  # Python调试器
import ipdb; ipdb.set_trace()  # IPython调试器（更友好）
```

### 2. 详细日志

```bash
# 设置日志级别为DEBUG
export LOG_LEVEL=DEBUG
```

### 3. 类型检查

```bash
# 运行mypy类型检查
mypy utils/
```

### 4. 代码格式化

```bash
# 格式化代码
black .

# 排序导入
isort .

# 检查代码风格
flake8 .
```

---

## 贡献指南

### 1. Fork & Clone

```bash
# Fork项目到你的账号
# Clone你的fork
git clone https://github.com/your-username/ComfyUI-UnlimitAI.git
cd ComfyUI-UnlimitAI

# 添加上游仓库
git remote add upstream https://github.com/original-repo/ComfyUI-UnlimitAI.git
```

### 2. 创建分支

```bash
# 创建功能分支
git checkout -b feature/your-feature-name

# 或创建修复分支
git checkout -b fix/your-bug-fix
```

### 3. 开发 & 测试

```bash
# 进行开发
# ...

# 运行测试
python run_tests.py

# 运行类型检查
mypy utils/

# 格式化代码
black .
isort .
```

### 4. 提交代码

```bash
# 提交更改
git add .
git commit -m "feat: 添加新功能"

# 推送到你的fork
git push origin feature/your-feature-name
```

### 5. 创建Pull Request

- 在GitHub上创建Pull Request
- 填写PR描述
- 等待代码审查
- 根据反馈修改

### 提交信息规范

```
feat: 新功能
fix: 修复bug
docs: 文档更新
style: 代码格式调整
refactor: 重构
test: 测试相关
chore: 构建/工具相关
```

---

## 常见问题

### Q: 如何添加新的模型支持？

1. 在 `config.yaml` 中添加模型配置
2. 在对应的节点中添加模型选项
3. 更新类型定义

### Q: 如何处理API频率限制？

使用智能延迟系统：

```python
from utils.delay import SmartDelay

delay = SmartDelay()
delay.wait("api_call")
```

### Q: 如何调试ComfyUI节点？

1. 在ComfyUI中启用开发者模式
2. 查看ComfyUI日志输出
3. 使用日志系统记录详细信息

### Q: 测试覆盖率如何提高？

1. 为新功能编写测试
2. 增加边界条件测试
3. 添加集成测试

---

## 相关资源

- [ComfyUI文档](https://github.com/comfyanonymous/ComfyUI)
- [UnlimitAI API文档](https://docs.unlimitai.com)
- [Python类型提示](https://docs.python.org/zh-cn/3/library/typing.html)
- [Pytest文档](https://docs.pytest.org/)
- [MyPy文档](https://mypy.readthedocs.io/)

---

## 联系方式

- **Issues**: https://github.com/your-repo/ComfyUI-UnlimitAI/issues
- **Discussions**: https://github.com/your-repo/ComfyUI-UnlimitAI/discussions

---

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。
