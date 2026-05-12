"""
内容去重模块

功能：
1. 基于内容哈希去重
2. 支持多种内容类型
3. 持久化缓存
4. 统计分析

使用方法:
    from utils.content_dedup import ContentDeduplicator
    
    dedup = ContentDeduplicator()
    result = dedup.get_or_generate(
        content=prompt,
        generate_func=lambda: generate_image(prompt),
        content_type="image"
    )
"""

import hashlib
import json
import time
import logging
from typing import Dict, Any, Callable, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
import threading

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """缓存条目"""
    content_hash: str
    content_type: str
    result: Dict[str, Any]
    created_at: float
    hits: int
    metadata: Optional[Dict] = None


class ContentDeduplicator:
    """
    内容去重器
    
    基于内容哈希避免重复生成
    
    Examples:
        >>> dedup = ContentDeduplicator()
        >>> 
        >>> # 第一次生成
        >>> result1 = dedup.get_or_generate(
        ...     content="A beautiful sunset",
        ...     generate_func=lambda: {"image_url": "http://..."},
        ...     content_type="image"
        ... )
        >>> print(result1["from_cache"])  # False
        >>> 
        >>> # 第二次相同内容（命中缓存）
        >>> result2 = dedup.get_or_generate(
        ...     content="A beautiful sunset",
        ...     generate_func=lambda: {"image_url": "http://..."},
        ...     content_type="image"
        ... )
        >>> print(result2["from_cache"])  # True
    """
    
    def __init__(
        self,
        cache_dir: str = "cache/dedup",
        enable_persistence: bool = True,
        max_cache_size: int = 1000
    ):
        """
        初始化
        
        Args:
            cache_dir: 缓存目录
            enable_persistence: 是否启用持久化
            max_cache_size: 最大缓存条目数
        """
        self.cache_dir = Path(cache_dir)
        self.enable_persistence = enable_persistence
        self.max_cache_size = max_cache_size
        
        self.cache: Dict[str, CacheEntry] = {}
        
        self._lock = threading.Lock()
        self._dirty = False
        self._dirty_count = 0
        
        self.stats = {
            "total_requests": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "evictions": 0
        }
        
        if self.enable_persistence:
            self._load_cache()
    
    def get_or_generate(
        self,
        content: str,
        generate_func: Callable[[], Dict[str, Any]],
        content_type: str = "image",
        metadata: Optional[Dict] = None,
        force_generate: bool = False
    ) -> Dict[str, Any]:
        """
        获取或生成内容
        
        Args:
            content: 内容描述（如prompt）
            generate_func: 生成函数
            content_type: 内容类型
            metadata: 元数据
            force_generate: 强制重新生成
        
        Returns:
            结果字典（包含 from_cache 字段）
        """
        self.stats["total_requests"] += 1
        
        # 生成内容哈希
        content_hash = self._generate_hash(content, content_type)
        cache_key = f"{content_type}_{content_hash}"
        
        # 检查缓存
        if not force_generate:
            cached_result = self._get_from_cache(cache_key)
            if cached_result is not None:
                self.stats["cache_hits"] += 1
                logger.info(f"缓存命中: {content_type} - {content_hash[:8]}")
                
                return {
                    **cached_result,
                    "from_cache": True,
                    "cache_key": cache_key
                }
        
        # 未命中缓存，生成新内容
        self.stats["cache_misses"] += 1
        logger.info(f"缓存未命中，生成新内容: {content_type} - {content_hash[:8]}")
        
        try:
            result = generate_func()
            
            # 存入缓存
            self._store_in_cache(
                cache_key=cache_key,
                content_hash=content_hash,
                content_type=content_type,
                result=result,
                metadata=metadata
            )
            
            return {
                **result,
                "from_cache": False,
                "cache_key": cache_key
            }
            
        except Exception as e:
            logger.error(f"生成失败: {e}")
            raise
    
    def _generate_hash(self, content: str, content_type: str) -> str:
        """生成内容哈希"""
        hash_data = f"{content_type}:{content}"
        return hashlib.sha256(hash_data.encode('utf-8')).hexdigest()
    
    def _get_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """从缓存获取"""
        with self._lock:
            entry = self.cache.get(cache_key)
            
            if entry:
                entry.hits += 1
                if self.enable_persistence:
                    self._dirty = True
                    self._dirty_count += 1
                return entry.result
            
            return None
    
    def _store_in_cache(
        self,
        cache_key: str,
        content_hash: str,
        content_type: str,
        result: Dict[str, Any],
        metadata: Optional[Dict] = None
    ):
        """存入缓存"""
        snapshot_to_write = None
        
        with self._lock:
            if len(self.cache) >= self.max_cache_size:
                self._evict_cache()
            
            entry = CacheEntry(
                content_hash=content_hash,
                content_type=content_type,
                result=result,
                created_at=time.time(),
                hits=0,
                metadata=metadata
            )
            
            self.cache[cache_key] = entry
            
            if self.enable_persistence:
                self._dirty = True
                self._dirty_count += 1
                
                if self._dirty_count >= 10:
                    snapshot_to_write = {k: e for k, e in self.cache.items()}
                    self._dirty = False
                    self._dirty_count = 0
        
        if snapshot_to_write is not None:
            self._write_cache_snapshot(snapshot_to_write)
    
    def _evict_cache(self):
        """清理缓存（LRU策略）"""
        if not self.cache:
            return
        
        # 找到最少使用的条目
        lru_key = min(
            self.cache.keys(),
            key=lambda k: (self.cache[k].hits, self.cache[k].created_at)
        )
        
        del self.cache[lru_key]
        self.stats["evictions"] += 1
        
        logger.debug(f"清理缓存: {lru_key}")
    
    def _load_cache(self):
        """加载缓存"""
        cache_file = self.cache_dir / "dedup_cache.json"
        
        if not cache_file.exists():
            return
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for key, entry_data in data.get("entries", {}).items():
                entry = CacheEntry(**entry_data)
                self.cache[key] = entry
            
            logger.info(f"加载缓存: {len(self.cache)} 条")
            
        except Exception as e:
            logger.warning(f"加载缓存失败: {e}")
    
    def save_cache(self):
        """保存全部缓存（持锁快照后写文件）。"""
        if not self.enable_persistence:
            return
        
        with self._lock:
            snapshot = {k: entry for k, entry in self.cache.items()}
            stats_snapshot = dict(self.stats)
        
        self._write_cache_snapshot(snapshot, stats_snapshot)
    
    def _write_cache_snapshot(self, snapshot: Dict[str, CacheEntry], stats_snapshot: Optional[Dict] = None):
        """将缓存快照写入磁盘（不持锁，可安全在锁内调用）。"""
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            cache_file = self.cache_dir / "dedup_cache.json"
            
            data = {
                "entries": {
                    key: {
                        "content_hash": entry.content_hash,
                        "content_type": entry.content_type,
                        "result": entry.result,
                        "created_at": entry.created_at,
                        "hits": entry.hits,
                        "metadata": entry.metadata
                    }
                    for key, entry in snapshot.items()
                },
                "stats": stats_snapshot or self.stats,
                "saved_at": time.time()
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"保存缓存: {len(snapshot)} 条")
            
        except Exception as e:
            logger.error(f"保存缓存失败: {e}")
    
    def check_exists(self, content: str, content_type: str = "image") -> Optional[Dict[str, Any]]:
        """
        检查缓存中是否存在
        
        Args:
            content: 内容描述
            content_type: 内容类型
            
        Returns:
            缓存的结果，不存在则None
        """
        content_hash = self._generate_hash(content, content_type)
        cache_key = f"{content_type}_{content_hash}"
        return self._get_from_cache(cache_key)
    
    def store(self, content: str, result: Dict[str, Any], content_type: str = "image", metadata: Optional[Dict] = None):
        """
        存入缓存
        
        Args:
            content: 内容描述
            result: 生成结果
            content_type: 内容类型
            metadata: 元数据
        """
        content_hash = self._generate_hash(content, content_type)
        cache_key = f"{content_type}_{content_hash}"
        self._store_in_cache(
            cache_key=cache_key,
            content_hash=content_hash,
            content_type=content_type,
            result=result,
            metadata=metadata
        )
    
    def flush(self):
        """将脏缓存数据批量写入磁盘。
        
        在锁内快照数据，释放锁后再写文件，避免死锁和长时间持锁。
        """
        if not self.enable_persistence:
            return
        
        snapshot = None
        with self._lock:
            if not self._dirty:
                return
            self._dirty = False
            self._dirty_count = 0
            snapshot = {k: entry for k, entry in self.cache.items()}
        
        if snapshot is not None:
            self._write_cache_snapshot(snapshot)
    
    def clear_cache(self):
        """清空缓存"""
        with self._lock:
            old_count = len(self.cache)
            self.cache.clear()
            self._dirty = False
            self._dirty_count = 0
            self.stats["evictions"] += old_count
        
        if self.enable_persistence:
            cache_file = self.cache_dir / "dedup_cache.json"
            if cache_file.exists():
                cache_file.unlink()
        
        logger.info("缓存已清空")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        total = max(self.stats["total_requests"], 1)
        
        return {
            **self.stats,
            "cache_size": len(self.cache),
            "hit_rate": self.stats["cache_hits"] / total,
            "miss_rate": self.stats["cache_misses"] / total,
            "cache_by_type": self._get_cache_by_type()
        }
    
    def _get_cache_by_type(self) -> Dict[str, int]:
        """按类型统计缓存"""
        by_type = {}
        for entry in self.cache.values():
            by_type[entry.content_type] = by_type.get(entry.content_type, 0) + 1
        return by_type
    
    def get_similar_content(
        self,
        content: str,
        content_type: str,
        similarity_threshold: float = 0.8
    ) -> Optional[Dict[str, Any]]:
        """
        查找相似内容（基于简单的文本相似度）
        
        Args:
            content: 内容描述
            content_type: 内容类型
            similarity_threshold: 相似度阈值
        
        Returns:
            相似内容结果，或 None
        """
        # 简单实现：基于关键词重叠
        content_words = set(content.lower().split())
        
        for key, entry in self.cache.items():
            if not key.startswith(content_type):
                continue
            
            # 获取原始内容（需要从metadata中获取）
            if not entry.metadata or "original_content" not in entry.metadata:
                continue
            
            original_content = entry.metadata["original_content"]
            original_words = set(original_content.lower().split())
            
            # 计算Jaccard相似度
            if not content_words or not original_words:
                continue
            
            intersection = len(content_words & original_words)
            union = len(content_words | original_words)
            similarity = intersection / union
            
            if similarity >= similarity_threshold:
                logger.info(f"找到相似内容: 相似度 {similarity:.2f}")
                return {
                    **entry.result,
                    "from_cache": True,
                    "similarity": similarity
                }
        
        return None


class BatchDeduplicator:
    """
    批量去重器
    
    优化批量场景的去重处理
    """
    
    def __init__(self, deduplicator: ContentDeduplicator):
        self.dedup = deduplicator
        self.batch_stats = {
            "total_scenes": 0,
            "unique_prompts": 0,
            "duplicates_found": 0
        }
    
    def deduplicate_scenes(
        self,
        scenes: list,
        content_field: str = "visual_prompt",
        content_type: str = "image"
    ) -> Tuple[list, Dict[str, Any]]:
        """
        批量去重场景
        
        Args:
            scenes: 场景列表
            content_field: 内容字段
            content_type: 内容类型
        
        Returns:
            (去重后的场景列表, 去重映射)
        """
        self.batch_stats["total_scenes"] = len(scenes)
        
        unique_content = {}  # {content_hash: scene_index}
        dedup_mapping = {}   # {original_index: unique_index}
        deduplicated_scenes = []
        
        for i, scene in enumerate(scenes):
            content = scene.get(content_field, "")
            
            if not content:
                deduplicated_scenes.append(scene)
                continue
            
            # 生成哈希
            content_hash = self.dedup._generate_hash(content, content_type)
            
            if content_hash in unique_content:
                # 重复内容
                unique_idx = unique_content[content_hash]
                dedup_mapping[i] = unique_idx
                self.batch_stats["duplicates_found"] += 1
                
                logger.info(f"场景 {i+1} 与场景 {unique_idx+1} 重复")
            else:
                # 唯一内容
                unique_content[content_hash] = i
                deduplicated_scenes.append(scene)
                self.batch_stats["unique_prompts"] += 1
        
        return deduplicated_scenes, {
            "mapping": dedup_mapping,
            "stats": self.batch_stats
        }
    
    def restore_duplicated_results(
        self,
        unique_results: list,
        dedup_info: Dict[str, Any]
    ) -> list:
        """
        恢复重复场景的结果
        
        Args:
            unique_results: 唯一场景的结果
            dedup_info: 去重信息
        
        Returns:
            完整结果列表
        """
        mapping = dedup_info["mapping"]
        total_scenes = dedup_info["stats"]["total_scenes"]
        
        # 创建完整结果列表
        full_results = [None] * total_scenes
        
        # 填充唯一结果
        unique_idx = 0
        for i in range(total_scenes):
            if i not in mapping:
                full_results[i] = unique_results[unique_idx]
                unique_idx += 1
        
        # 填充重复结果
        for dup_idx, unique_idx in mapping.items():
            full_results[dup_idx] = unique_results[unique_idx]
        
        return full_results
