# スケルトン: エラーハンドリング (handlers/error_handler.py)

## 概要

アプリケーション全体のユーザー向けエラーメッセージ生成を一元管理するモジュール。
全メソッドは `@staticmethod` なので、インスタンス化不要で `ErrorHandler.handle_xxx()` として呼び出す。
ログ出力は各モジュールが `_logger = logging.getLogger(__name__)` で直接行い、このクラスは行わない。
業務ドメインに応じてエラーハンドリングメソッドを追加する。

## ファイル配置

`handlers/error_handler.py`

## スケルトンコード

```python
"""エラーハンドリング関連のモジュール"""
from typing import Optional


class LoopLimitError(RuntimeError):
    """
    エージェントReActループの制限エラー

    エージェントのループが最大回数に達した場合に発生します。
    """

    def __init__(self, current_iteration: int, max_iterations: int, agent_name: str):
        """
        初期化

        Args:
            current_iteration: 現在のループ回数
            max_iterations: 最大ループ回数
            agent_name: エージェント名
        """
        self.current_iteration = current_iteration
        self.max_iterations = max_iterations
        self.agent_name = agent_name
        # TODO: 詳細設計書に従い実装
        # - エージェント名とループ回数情報を含む日本語メッセージを生成
        # - 親クラスの__init__にメッセージを渡す
        pass


class ErrorHandler:
    """エラーハンドリングヘルパー関数クラス

    例外オブジェクトを受け取り、ユーザー向け日本語エラーメッセージ文字列を生成して返す。
    ログ出力は行わない（呼び出し元モジュールが _logger 経由でログを出力すること）。

    全メソッドは @staticmethod なので、インスタンス化不要で ErrorHandler.handle_xxx() として呼び出せる。
    """

    # ============ 共通エラーハンドリングメソッド ============

    @staticmethod
    def handle_keyboard_interrupt(error: Optional[Exception] = None) -> str:
        """
        キーボード中断（Ctrl+C）の処理

        Args:
            error: 発生した例外オブジェクト（省略可）

        Returns:
            str: ユーザー向けメッセージ
        """
        # TODO: 詳細設計書に従い実装
        # - 処理中断を示す日本語メッセージの返却
        pass

    @staticmethod
    def handle_loop_limit_error(error: "LoopLimitError") -> str:
        """
        ループ上限到達エラーの処理

        Args:
            error: LoopLimitErrorオブジェクト

        Returns:
            str: ユーザー向けエラーメッセージ
        """
        # TODO: 詳細設計書に従い実装
        # - 上限到達を知らせる日本語メッセージの返却
        pass

    @staticmethod
    def handle_validation_error(error: Exception) -> str:
        """
        Pydantic ValidationErrorの処理

        Args:
            error: 発生した例外オブジェクト（ValidationError）

        Returns:
            str: ユーザー向け日本語エラーメッセージ
        """
        # TODO: 詳細設計書に従い実装
        # - error.errors() でフィールドごとのエラー情報を解析
        # - 日本語のバリデーションエラーメッセージを生成して返却
        pass

    @staticmethod
    def handle_runtime_error(error: Optional[Exception] = None) -> str:
        """
        RuntimeErrorの処理

        Args:
            error: 発生した例外オブジェクト（省略可）

        Returns:
            str: ユーザー向けエラーメッセージ
        """
        # TODO: 詳細設計書に従い実装
        pass

    @staticmethod
    def handle_unexpected_error(error: Optional[Exception] = None) -> str:
        """
        予期しないエラーの処理

        Args:
            error: 発生した例外オブジェクト（省略可）

        Returns:
            str: ユーザー向けエラーメッセージ
        """
        # TODO: 詳細設計書に従い実装
        # - システム障害を知らせる日本語メッセージの返却
        pass

    # ============ ドメイン固有エラーハンドリングメソッド ============
    # 業務ドメインに応じてエラーハンドリングメソッドを追加する

    # TODO: 業務ドメイン固有のエラーハンドラを追加
    # 例:
    # @staticmethod
    # def handle_{domain}_error(error: Optional[Exception] = None) -> str:
    #     """
    #     {ドメイン固有}エラーの処理
    #
    #     Args:
    #         error: 発生した例外オブジェクト（省略可）
    #
    #     Returns:
    #         str: ユーザー向けエラーメッセージ
    #     """
    #     pass
```

## カスタマイズガイド

1. **@staticmethod**: 全メソッドは `@staticmethod` で定義し、インスタンス化不要とする
2. **ログ出力なし**: このクラスはログを出力しない。呼び出し元が `_logger = logging.getLogger(__name__)` でログを出力する
3. **ドメイン固有エラーハンドラ**: 業務要件に応じて `handle_{domain}_error()` メソッドを `@staticmethod` で追加する
4. **エラーメッセージ**: ユーザー向けメッセージは全て日本語で、技術的な詳細を含めない
