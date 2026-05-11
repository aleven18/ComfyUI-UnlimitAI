# 项目结构

本文档展示ComfyUI-UnlimitAI的目录结构和文件组织。

---

## 📁 目录结构

```
ComfyUI-UnlimitAI/
├── 📄 README.md                   # 项目说明文档
├── 📄 LICENSE                     # MIT许可证
├── 📄 CHANGELOG.md                # 版本更新日志
├── 📄 CONTRIBUTING.md             # 贡献指南
├── 📄 DEVELOPMENT.md              # 开发指南
├── 📄 __init__.py                 # ComfyUI插件入口
│
├── ⚙️ 配置文件
│   ├── config.yaml                # 主配置文件
│   ├── .env.example               # 环境变量模板
│   ├── .gitignore                 # Git忽略规则
│   ├── pytest.ini                 # Pytest配置
│   ├── mypy.ini                   # MyPy配置
│   ├── requirements.txt           # 生产依赖
│   └── requirements-dev.txt       # 开发依赖
│
├── 🎯 节点模块 (nodes/)
│   ├── text_nodes.py              # 文本生成节点 (6个)
│   ├── image_nodes.py             # 图像生成节点 (7个)
│   ├── video_nodes.py             # 视频生成节点 (10个)
│   ├── audio_nodes.py             # 音频生成节点 (7个)
│   ├── music_nodes.py             # 音乐生成节点 (6个)
│   ├── workflow_nodes.py          # 工作流节点 (5个)
│   ├── config_nodes.py            # 配置节点 (3个)
│   ├── optimized_nodes.py         # 优化节点 (4个)
│   ├── advanced_nodes.py          # 高级节点 (7个)
│   ├── character_nodes.py         # 角色节点
│   └── character_nodes_optimized.py # 优化版角色节点 (4个)
│
├── 🛠️ 工具模块 (utils/)
│   ├── api_client.py              # API客户端
│   ├── api_client.pyi             # API客户端类型存根
│   ├── config.py                  # 配置管理
│   ├── logger.py                  # 日志系统
│   ├── exceptions.py              # 异常处理
│   ├── delay.py                   # 智能延迟
│   ├── types.py                   # 类型定义
│   ├── persistent_storage.py      # 持久化存储
│   ├── cost_optimizer.py          # 成本优化
│   └── helpers.py                 # 辅助函数
│
├── 🧪 测试 (tests/)
│   ├── conftest.py                # 测试配置和fixtures
│   ├── test_utils.py              # 工具模块测试 (40个)
│   ├── test_api_client.py         # API客户端测试 (26个)
│   ├── test_character_nodes.py    # 角色节点测试 (20个)
│   ├── test_nodes_basic.py        # 节点基础测试 (30个)
│   ├── test_persistent_storage.py # 存储模块测试 (19个)
│   ├── test_workflows.py          # 工作流测试 (26个)
│   └── README.md                  # 测试指南
│
├── 📚 文档 (docs/)
│   ├── guides/                    # 指南文档
│   │   ├── ADVANCED_FEATURES_GUIDE.md
│   │   ├── CHARACTER_MANAGEMENT_GUIDE.md
│   │   ├── WORKFLOW_GUIDE.md
│   │   └── ... (其他指南)
│   │
│   ├── reports/                   # 项目报告
│   │   ├── CHARACTER_IMPLEMENTATION_REPORT.md
│   │   ├── DEEP_OPTIMIZATION_ANALYSIS.md
│   │   ├── OPTIMIZATION_SUMMARY.md
│   │   └── ... (其他报告)
│   │
│   ├── api/                       # API文档
│   ├── TODO.md                    # 待办事项
│   └── WORKFLOW_GUIDE.md          # 工作流使用指南
│
├── 🎬 工作流 (workflows/)
│   ├── budget_workflow.json       # 成本优化工作流
│   ├── balanced_workflow.json     # 平衡工作流
│   ├── quality_workflow.json      # 质量优先工作流
│   ├── max_quality_workflow.json  # 极致质量工作流
│   ├── novel_to_drama_workflow.json
│   └── ... (其他工作流JSON)
│
├── ⚡ 工作流配置 (workflow_configs/)
│   ├── budget_config.json
│   ├── balanced_config.json
│   ├── quality_config.json
│   └── max_quality_config.json
│
├── 🔧 脚本 (scripts/)
│   ├── check_project.py           # 项目检查脚本
│   ├── check_workflows.py         # 工作流验证脚本
│   ├── test_cost_optimization.py  # 成本优化测试
│   └── start.sh                   # 启动脚本
│
├── 🏃 运行脚本
│   └── run_tests.py               # 测试运行脚本
│
└── 📦 其他
    └── web/                       # Web界面资源（可选）
```

---

## 📊 文件统计

### 代码文件

| 类型 | 数量 | 说明 |
|------|------|------|
| **Python节点文件** | 11个 | 自定义ComfyUI节点 |
| **Python工具文件** | 10个 | 核心工具模块 |
| **测试文件** | 6个 | 单元测试和集成测试 |
| **配置文件** | 8个 | 项目配置和工具配置 |
| **脚本文件** | 4个 | 实用脚本 |

### 文档文件

| 类型 | 数量 | 位置 |
|------|------|------|
| **核心文档** | 4个 | 根目录 |
| **指南文档** | 10+ | docs/guides/ |
| **报告文档** | 10+ | docs/reports/ |
| **工作流文档** | 1个 | docs/ |

### 工作流文件

| 类型 | 数量 | 说明 |
|------|------|------|
| **工作流JSON** | 10+ | ComfyUI工作流定义 |
| **配置JSON** | 4个 | 工作流配置 |

---

## 🎯 目录用途说明

### /nodes/ - 节点模块
存放所有ComfyUI自定义节点，每个节点文件对应一类功能。

**关键文件**:
- `character_nodes_optimized.py`: 优化后的角色管理节点
- `text_nodes.py`: 文本生成相关节点
- `image_nodes.py`: 图像生成相关节点

### /utils/ - 工具模块
核心功能模块，提供API客户端、日志、异常处理等基础服务。

**关键文件**:
- `api_client.py`: 统一API客户端
- `logger.py`: 日志系统
- `exceptions.py`: 异常处理体系

### /tests/ - 测试
所有测试文件，包括单元测试、集成测试和测试配置。

**关键文件**:
- `conftest.py`: 测试配置和共享fixtures
- `test_*.py`: 各模块的测试文件

### /docs/ - 文档
项目文档，包括用户指南、开发指南和项目报告。

**子目录**:
- `guides/`: 使用指南和教程
- `reports/`: 项目分析和实施报告
- `api/`: API参考文档

### /workflows/ - 工作流
ComfyUI工作流JSON文件，可直接在ComfyUI中加载使用。

**关键文件**:
- `balanced_workflow.json`: 推荐日常使用
- `budget_workflow.json`: 成本优化版本

### /workflow_configs/ - 工作流配置
工作流的参数配置文件，定义模型选择和生成参数。

### /scripts/ - 脚本
实用脚本和工具，用于项目检查、验证等。

---

## 🚀 快速导航

### 新手入门
1. 阅读 [README.md](../README.md) 了解项目
2. 查看 [WORKFLOW_GUIDE.md](WORKFLOW_GUIDE.md) 学习使用
3. 尝试运行 `workflows/balanced_workflow.json`

### 开发者
1. 阅读 [DEVELOPMENT.md](../DEVELOPMENT.md) 了解开发规范
2. 查看 [CONTRIBUTING.md](../CONTRIBUTING.md) 学习贡献流程
3. 运行测试: `python run_tests.py`

### 高级用户
1. 查看 `docs/guides/` 中的高级功能指南
2. 自定义工作流配置
3. 集成到自己的项目

---

## 📝 文件命名规范

### Python文件
- 模块: 小写下划线 (如: `api_client.py`)
- 类: 大驼峰 (如: `UnlimitAIClient`)
- 函数: 小写下划线 (如: `generate_text`)

### 文档文件
- 大写开头 (如: `README.md`, `DEVELOPMENT.md`)
- 或小写加下划线 (如: `workflow_guide.md`)

### 配置文件
- 点开头或小写 (如: `.env.example`, `config.yaml`)

### 工作流文件
- 小写加下划线 (如: `budget_workflow.json`)

---

## 🔄 目录变更历史

### 2025-01-XX - 项目结构优化
- ✅ 清理编译文件 (__pycache__, *.pyc)
- ✅ 整理报告文件到 docs/reports/
- ✅ 整理指南文档到 docs/guides/
- ✅ 移动脚本文件到 scripts/
- ✅ 清理工作流目录中的文档文件
- ✅ 创建清晰的目录结构

---

## 🎊 总结

项目结构已经过优化，具有以下特点：

✅ **清晰的组织**: 按功能分类，易于导航
✅ **规范的命名**: 遵循Python和社区规范
✅ **完善的文档**: 详细的使用和开发指南
✅ **便于维护**: 模块化设计，职责明确

---

**最后更新**: 2025-01-XX
