# 测试指南

## 快速开始

### 安装测试依赖

```bash
pip install -r requirements-dev.txt
```

### 运行测试

```bash
# 运行所有单元测试
python run_tests.py

# 或者使用pytest直接运行
pytest tests/

# 运行特定测试文件
pytest tests/test_api_client.py

# 运行特定测试类
pytest tests/test_api_client.py::TestUnlimitAIClient

# 运行特定测试方法
pytest tests/test_api_client.py::TestUnlimitAIClient::test_generate_text_success
```

## 测试类型

### 单元测试（Unit Tests）

快速、独立的测试，不依赖外部服务。

```bash
pytest tests/ -m unit
```

### 集成测试（Integration Tests）

测试多个组件的集成。

```bash
pytest tests/ -m integration --run-integration
```

### API测试（API Tests）

需要真实API访问的测试。

```bash
# 设置API Key
export UNITED_API_KEY="your_api_key"

# 运行API测试
pytest tests/ -m api --run-api
```

### 慢速测试（Slow Tests）

运行时间较长的测试。

```bash
pytest tests/ -m slow --run-slow
```

## 覆盖率报告

### 生成覆盖率报告

```bash
# 终端输出
pytest tests/ --cov=. --cov-report=term-missing

# HTML报告
pytest tests/ --cov=. --cov-report=html:htmlcov

# 使用脚本
python run_tests.py --cov-report=html
```

### 查看HTML报告

```bash
# macOS
open htmlcov/index.html

# Linux
xdg-open htmlcov/index.html

# Windows
start htmlcov/index.html
```

## 测试覆盖率目标

- **最低覆盖率**: 50%
- **推荐覆盖率**: 80%
- **核心模块覆盖率**: 90%+

## 编写测试

### 测试命名规范

```
test_<module_name>.py          # 测试文件名
Test<ClassName>               # 测试类名
test_<method_name>            # 测试方法名
```

### 测试结构

```python
class TestFeatureName:
    """功能测试"""
    
    @pytest.fixture
    def setup(self):
        """测试前准备"""
        pass
    
    def test_success_case(self, setup):
        """测试成功场景"""
        pass
    
    def test_failure_case(self, setup):
        """测试失败场景"""
        pass
```

### 使用Fixtures

```python
# 使用内置fixture
def test_with_sample_data(sample_character_data):
    assert sample_character_data["name"] == "小明"

# 使用mock
def test_with_mock(mock_api_client):
    result = mock_api_client.generate_text("test")
    assert result == "生成的文本"
```

### 标记测试

```python
import pytest

@pytest.mark.unit
def test_unit():
    """单元测试"""
    pass

@pytest.mark.integration
def test_integration():
    """集成测试"""
    pass

@pytest.mark.slow
def test_slow():
    """慢速测试"""
    pass

@pytest.mark.api
def test_api():
    """API测试"""
    pass
```

## 持续集成

### GitHub Actions

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run tests
      run: pytest tests/ --cov=. --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

## 故障排除

### 测试失败

1. 检查错误信息
2. 查看测试日志
3. 使用`-v`参数获取详细信息
4. 使用`--tb=long`获取完整回溯

### 导入错误

```bash
# 确保在项目根目录
cd /path/to/project

# 检查PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### 依赖问题

```bash
# 重新安装依赖
pip install -r requirements-dev.txt --force-reinstall
```

## 最佳实践

1. **独立性**: 每个测试应该独立运行
2. **可重复性**: 测试结果应该可重复
3. **快速**: 单元测试应该快速执行
4. **清晰**: 测试意图应该清晰明了
5. **覆盖**: 测试应该覆盖各种场景（成功、失败、边界）

## 参考资料

- [Pytest文档](https://docs.pytest.org/)
- [Coverage.py文档](https://coverage.readthedocs.io/)
- [Python测试最佳实践](https://docs.python-guide.org/writing/tests/)
