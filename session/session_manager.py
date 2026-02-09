"""セッション管理機能

FileSessionManagerを使用してエージェントの会話履歴と状態を永続化します。
"""
import os
import uuid
from pathlib import Path
from datetime import datetime
from strands.session.file_session_manager import FileSessionManager


class SessionManagerFactory:
    """セッションマネージャーのファクトリークラス"""
    
    # セッションの保存先ディレクトリ
    _storage_dir = None
    
    @classmethod
    def generate_session_id(cls, prefix: str = "") -> str:
        """
        一意のセッションIDを生成
        
        セッションIDはタイムスタンプ（秒単位）とUUID（8文字）の組み合わせで生成されます。
        これにより、同じ秒に複数のセッションが開始されても衝突を防ぎます。
        
        Args:
            prefix: セッションIDのプレフィックス（オプション）
                   例: "test", "user_a" など
        
        Returns:
            str: 生成されたセッションID
                - prefixなし: "YYYYMMDD_HHMMSS_uuid8"
                - prefixあり: "prefix_YYYYMMDD_HHMMSS_uuid8"
        
        Examples:
            >>> SessionManagerFactory.generate_session_id()
            "20260209_143022_a1b2c3d4"
            
            >>> SessionManagerFactory.generate_session_id("test")
            "test_20260209_143022_a1b2c3d4"
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        
        if prefix:
            return f"{prefix}_{timestamp}_{unique_id}"
        return f"{timestamp}_{unique_id}"
    
    @classmethod
    def get_storage_dir(cls) -> str:
        """セッションの保存先ディレクトリを取得"""
        if cls._storage_dir is None:
            # プロジェクトルートのstorageディレクトリを使用
            project_root = Path(__file__).parent.parent
            cls._storage_dir = str(project_root / "storage" / "sessions")
            
            # ディレクトリが存在しない場合は作成
            os.makedirs(cls._storage_dir, exist_ok=True)
        
        return cls._storage_dir
    
    @classmethod
    def create_session_manager(cls, session_id: str) -> FileSessionManager:
        """
        FileSessionManagerのインスタンスを作成
        
        Args:
            session_id: セッションID（ユーザーごとに一意）
        
        Returns:
            FileSessionManager: セッションマネージャーのインスタンス
        """
        storage_dir = cls.get_storage_dir()
        
        return FileSessionManager(
            session_id=session_id,
            storage_dir=storage_dir
        )
    
    @classmethod
    def get_session_path(cls, session_id: str) -> str:
        """
        指定されたセッションIDのセッションディレクトリパスを取得
        
        Args:
            session_id: セッションID
        
        Returns:
            str: セッションディレクトリのパス
        """
        storage_dir = cls.get_storage_dir()
        return os.path.join(storage_dir, f"session_{session_id}")
