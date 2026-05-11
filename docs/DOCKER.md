# Docker部署指南

本文档介绍如何使用Docker部署ComfyUI-UnlimitAI。

---

## 🚀 快速开始

### 使用Docker Compose（推荐）

```bash
# 1. 克隆项目
git clone https://github.com/your-repo/ComfyUI-UnlimitAI.git
cd ComfyUI-UnlimitAI

# 2. 创建环境变量文件
cp .env.example .env
# 编辑.env填写API密钥

# 3. 启动服务
docker-compose up -d

# 4. 查看日志
docker-compose logs -f

# 5. 访问服务
open http://localhost:8188
```

### 仅使用Docker

```bash
# 构建镜像
docker build -t comfyui-unlimitai:latest .

# 运行容器
docker run -d \
  --name comfyui-unlimitai \
  -p 8188:8188 \
  -e UNITED_API_KEY=your_api_key \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/output:/app/output \
  comfyui-unlimitai:latest
```

---

## 📋 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `UNITED_API_KEY` | UnlimitAI API密钥 | 必需 |
| `LOG_LEVEL` | 日志级别 | INFO |
| `MAX_WORKERS` | 最大工作进程数 | 4 |
| `CACHE_TTL` | 缓存TTL（秒） | 3600 |

---

## 🗂️ 目录挂载

| 容器路径 | 主机路径 | 说明 |
|---------|---------|------|
| `/app/data` | `./data` | 数据存储 |
| `/app/output` | `./output` | 输出文件 |
| `/app/logs` | `./logs` | 日志文件 |
| `/app/models` | `comfyui-models` | 模型文件 |

---

## 🔧 服务配置

### 基础服务

```yaml
# 仅ComfyUI
docker-compose up -d comfyui-unlimitai
```

### 完整服务栈

```yaml
# ComfyUI + Redis + PostgreSQL
docker-compose up -d
```

---

## 📊 性能优化

### 资源限制

```yaml
deploy:
  resources:
    reservations:
      cpus: '2'
      memory: 4G
    limits:
      cpus: '4'
      memory: 8G
```

### GPU支持

```yaml
services:
  comfyui-unlimitai:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

---

## 🛠️ 常用命令

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 查看日志
docker-compose logs -f

# 进入容器
docker-compose exec comfyui-unlimitai bash

# 清理数据
docker-compose down -v
```

---

## 🔒 安全建议

1. **不要在镜像中硬编码API密钥**
2. **使用环境变量或密钥管理服务**
3. **定期更新基础镜像**
4. **使用非root用户运行**
5. **限制容器资源**

---

## 📖 更多信息

- [Docker官方文档](https://docs.docker.com/)
- [Docker Compose文档](https://docs.docker.com/compose/)
- [项目README](../README.md)

---

**最后更新**: 2025-01-XX
