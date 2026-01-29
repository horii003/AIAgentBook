"""セッション管理機能

FileSessionManagerを使用してエージェントの会話履歴と状態を永続化します。
"""
import os
from pathlib import Path
from strands.session.file_session_manager import FileSessionManager


class SessionManagerFactory:
    """セッションマネージャーのファクトリークラス"""
    
    # セッションの保存先ディレクトリ
    _storage_dir = None
    
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
