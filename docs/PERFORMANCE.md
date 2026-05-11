# 性能优化指南

本文档提供ComfyUI-UnlimitAI的性能优化建议和最佳实践。

---

## 📋 目录

- [性能概述](#性能概述)
- [优化策略](#优化策略)
- [最佳实践](#最佳实践)
- [性能监控](#性能监控)
- [故障排除](#故障排除)

---

## 性能概述

### 性能指标

| 操作 | 预期时间 | 优化后时间 |
|------|---------|-----------|
| 文本生成 | 2-5秒 | 1-3秒 |
| 图像生成 | 10-30秒 | 5-15秒 |
| 视频生成 | 60-180秒 | 30-90秒 |
| 音频生成 | 3-10秒 | 2-5秒 |

### 性能影响因素

1. **API响应时间** - 取决于模型和服务商
2. **网络延迟** - 取决于地理位置
3. **并发请求** - 频率限制会影响
4. **缓存命中率** - 重复请求可缓存

---

## 优化策略

### 1. 模型选择优化

#### 文本模型

```python
# 成本优化：使用DeepSeek
client.generate_text(
    prompt="...",
    model="deepseek-chat"  # 最快最便宜
)

# 质量优化：使用GPT-4
client.generate_text(
    prompt="...",
    model="gpt-4-turbo"  # 质量更高
)
```

#### 图像模型

```python
# 快速生成
client.generate_image(
    prompt="...",
    model="flux.1-schnell",  # 4步快速
    steps=4
)

# 高质量
client.generate_image(
    prompt="...",
    model="flux.1-dev",  # 更多细节
    steps=20
)
```

### 2. 并发处理

```python
import asyncio
from utils.api_client import UnlimitAIClient

async def parallel_generation(prompts):
    """并行生成多个内容"""
    client = UnlimitAIClient(api_key="...")
    
    tasks = [
        client.generate_text_async(prompt)
        for prompt in prompts
    ]
    
    results = await asyncio.gather(*tasks)
    return results
```

### 3. 智能缓存

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def cached_generation(prompt, model):
    """缓存生成结果"""
    client = UnlimitAIClient(api_key="...")
    return client.generate_text(prompt, model)
```

### 4. 智能延迟

```python
from utils.delay import SmartDelay

delay = SmartDelay(
    initial_delay=0.5,
    max_delay=10.0
)

for item in items:
    delay.wait("api_call")
    result = api_call(item)
    delay.on_success()
```

### 5. 批量处理

```python
def batch_process(items, batch_size=5):
    """批量处理"""
    results = []
    
    for i in range(0, len(items), batch_size):
        batch = items[i:i+batch_size]
        batch_results = process_batch(batch)
        results.extend(batch_results)
    
    return results
```

---

## 最佳实践

### 1. 提示词优化

```python
# ❌ 差的提示词
prompt = "画一个女孩"

# ✅ 好的提示词
prompt = """
一个穿着蓝色碎花连衣裙的年轻女孩，
站在樱花树下，微风拂过，花瓣飘落，
温暖的午后阳光，日系动漫风格，
柔和色调，高清细节
"""
```

### 2. 参数调优

```python
# 文本生成
client.generate_text(
    prompt="...",
    temperature=0.7,    # 平衡创造性和一致性
    max_tokens=500,     # 控制长度
    top_p=0.9          # 多样性
)

# 图像生成
client.generate_image(
    prompt="...",
    steps=4,            # 快速生成
    guidance=3.5,       # 平衡创造性和一致性
    size="1024x1024"    # 合适尺寸
)
```

### 3. 资源管理

```python
# 使用上下文管理器
with UnlimitAIClient(api_key="...") as client:
    result = client.generate_text("...")
    # 自动清理资源
```

---

## 性能监控

### 使用基准测试

```bash
# 运行性能测试
python scripts/benchmark.py

# 查看结果
# - 平均响应时间
# - 最小/最大时间
# - 标准差
```

### 监控指标

```python
import time
from utils.logger import get_logger

logger = get_logger("performance")

def monitored_operation():
    start = time.time()
    
    try:
        result = operation()
        elapsed = time.time() - start
        
        logger.info(f"操作完成，耗时: {elapsed:.2f}秒")
        return result
        
    except Exception as e:
        elapsed = time.time() - start
        logger.error(f"操作失败，耗时: {elapsed:.2f}秒", exc_info=True)
        raise
```

---

## 故障排除

### 常见性能问题

#### 1. API响应慢

**原因**:
- 网络延迟
- 服务器负载高
- 请求参数复杂

**解决方案**:
```python
# 使用更快的模型
client.generate_text(
    prompt="...",
    model="deepseek-chat"  # 比GPT-4快
)

# 减少max_tokens
client.generate_text(
    prompt="...",
    max_tokens=100  # 更快
)
```

#### 2. 频率限制

**原因**:
- API调用过于频繁
- 超出配额

**解决方案**:
```python
from utils.delay import SmartDelay, RateLimiter

# 使用智能延迟
delay = SmartDelay()
delay.wait("api_call")

# 使用频率限制器
limiter = RateLimiter(max_calls=10, period=1.0)
limiter.acquire()
```

#### 3. 内存占用高

**原因**:
- 缓存过多
- 并发请求多

**解决方案**:
```python
# 限制缓存大小
@lru_cache(maxsize=32)  # 减小缓存

# 清理缓存
cached_generation.cache_clear()
```

---

## 性能优化检查清单

- [ ] 使用合适的模型（成本vs质量）
- [ ] 优化提示词长度和清晰度
- [ ] 实现智能缓存机制
- [ ] 使用并行处理提高效率
- [ ] 配置智能延迟避免频率限制
- [ ] 监控性能指标
- [ ] 定期运行基准测试
- [ ] 清理临时文件和缓存
- [ ] 更新依赖到最新版本
- [ ] 使用CDN或就近服务器

---

## 更多资源

- [API参考](docs/api/API_REFERENCE.md)
- [故障排除](docs/TROUBLESHOOTING.md)
- [最佳实践](docs/guides/BEST_PRACTICES.md)

---

**最后更新**: 2025-01-XX
