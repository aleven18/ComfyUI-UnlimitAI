#!/usr/bin/env python3
"""
备份和恢复工具

提供数据备份、恢复和迁移功能。
"""

import json
import shutil
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class BackupManager:
    """备份管理器"""
    
    def __init__(self, data_dir: str = "data", backup_dir: str = "backups"):
        self.data_dir = Path(data_dir)
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
    
    def create_backup(self, name: str = None) -> str:
        """创建备份"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = name or f"backup_{timestamp}"
        backup_path = self.backup_dir / backup_name
        
        logger.info(f"创建备份: {backup_path}")
        
        # 复制数据目录
        if self.data_dir.exists():
            shutil.copytree(self.data_dir, backup_path / "data")
        
        # 创建备份元数据
        metadata = {
            "name": backup_name,
            "created_at": datetime.now().isoformat(),
            "data_dir": str(self.data_dir)
        }
        
        with open(backup_path / "metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"备份创建成功: {backup_path}")
        return str(backup_path)
    
    def restore_backup(self, backup_name: str):
        """恢复备份"""
        backup_path = self.backup_dir / backup_name
        
        if not backup_path.exists():
            raise FileNotFoundError(f"备份不存在: {backup_path}")
        
        logger.info(f"恢复备份: {backup_path}")
        
        # 恢复数据
        backup_data = backup_path / "data"
        if backup_data.exists():
            if self.data_dir.exists():
                shutil.rmtree(self.data_dir)
            shutil.copytree(backup_data, self.data_dir)
        
        logger.info("备份恢复成功")
    
    def list_backups(self) -> list:
        """列出所有备份"""
        backups = []
        for backup in self.backup_dir.iterdir():
            if backup.is_dir():
                metadata_file = backup / "metadata.json"
                if metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    backups.append(metadata)
        return sorted(backups, key=lambda x: x['created_at'], reverse=True)


if __name__ == "__main__":
    import sys
    
    manager = BackupManager()
    
    if len(sys.argv) < 2:
        print("用法:")
        print("  python backup.py create [name]")
        print("  python backup.py restore <name>")
        print("  python backup.py list")
        sys.exit(0)
    
    command = sys.argv[1]
    
    if command == "create":
        name = sys.argv[2] if len(sys.argv) > 2 else None
        manager.create_backup(name)
    
    elif command == "restore":
        if len(sys.argv) < 3:
            print("请指定备份名称")
            sys.exit(1)
        manager.restore_backup(sys.argv[2])
    
    elif command == "list":
        backups = manager.list_backups()
        for backup in backups:
            print(f"{backup['name']}: {backup['created_at']}")
