# スケルトン: セッション管理 (session/session_manager.py)

## 概要

FileSessionManagerを使用してエージェントの会話履歴と状態を永続化する。
全プロジェクトで共通利用できる汎用モジュール。

## ファイル配置

`session/session_manager.py`

## スケルトンコード

```python
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
        # TODO: 詳細設計書に従い実装
        # - タイムスタンプの生成
        # - UUIDの生成（先頭8文字）
        # - prefixの有無に応じたID文字列の構築
        # - IDの返却
        pass

    @classmethod
    def get_storage_dir(cls) -> str:
        """セッションの保存先ディレクトリを取得"""
        # TODO: 詳細設計書に従い実装
        # - キャッシュ確認（_storage_dir）
        # - プロジェクトルートからのパス構築
        # - ディレクトリの自動作成
        # - パスの返却
        pass

    @classmethod
    def create_session_manager(cls, session_id: str) -> FileSessionManager:
        """
        FileSessionManagerのインスタンスを作成

        Args:
            session_id: セッションID（ユーザーごとに一意）

        Returns:
            FileSessionManager: セッションマネージャーのインスタンス
        """
        # TODO: 詳細設計書に従い実装
        # - ストレージディレクトリの取得
        # - FileSessionManagerインスタンスの生成と返却
        pass

    @classmethod
    def get_session_path(cls, session_id: str) -> str:
        """
        指定されたセッションIDのセッションディレクトリパスを取得

        Args:
            session_id: セッションID

        Returns:
            str: セッションディレクトリのパス
        """
        # TODO: 詳細設計書に従い実装
        # - ストレージディレクトリの取得
        # - セッションサブディレクトリパスの構築と返却
        pass
```

## カスタマイズガイド

- このモジュールは汎用的なため、基本的にカスタマイズ不要
- セッション保存先のパスはプロジェクト要件に応じて変更可能
