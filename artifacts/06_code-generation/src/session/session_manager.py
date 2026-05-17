"""セッション管理

FileSessionManagerのラッパーとして、セッションID生成・セッション管理を提供する。
"""

import os
import uuid
from datetime import datetime
from pathlib import Path

from strands.session import FileSessionManager

_STORAGE_DIR = Path("storage/sessions")


class SessionManagerFactory:
    """セッション管理ファクトリ（全メソッド @staticmethod）"""

    @staticmethod
    def generate_session_id() -> str:
        """タイムスタンプ+UUID8文字形式のセッションIDを生成する"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        short_uuid = uuid.uuid4().hex[:8]
        return f"{timestamp}_{short_uuid}"

    @staticmethod
    def create_session_manager(session_id: str) -> FileSessionManager:
        """FileSessionManagerインスタンスを生成する"""
        session_dir = _STORAGE_DIR / f"session_{session_id}"
        session_dir.mkdir(parents=True, exist_ok=True)
        return FileSessionManager(session_id=session_id, storage_dir=str(session_dir))

    @staticmethod
    def session_exists(session_id: str) -> bool:
        """セッションの存在を確認する"""
        session_dir = _STORAGE_DIR / f"session_{session_id}"
        return session_dir.exists()

    @staticmethod
    def get_session_dir(session_id: str) -> str:
        """セッションディレクトリパスを取得する"""
        return str(_STORAGE_DIR / f"session_{session_id}")
