"""エラーハンドリング関連のモジュール。

全エージェント・全ツールで発生する例外を分類し、
ユーザー向けの日本語エラーメッセージを生成して返す。
ログ出力は各モジュールが _logger 経由で行い、このクラスは行わない。
"""
from typing import Optional


class LoopLimitError(RuntimeError):
    """エージェントReActループの制限エラー。

    エージェントのループが最大回数に達した場合に発生する。
    """

    def __init__(self, current_iteration: int, max_iterations: int, agent_name: str):
        """初期化。

        Args:
            current_iteration: 現在のループ回数
            max_iterations: 最大ループ回数
            agent_name: エージェント名
        """
        self.current_iteration = current_iteration
        self.max_iterations = max_iterations
        self.agent_name = agent_name
        message = (
            f"{agent_name} のループが最大回数（{max_iterations}回）に達しました。"
            f"（現在: {current_iteration}回）"
        )
        super().__init__(message)


class ErrorHandler:
    """エラーハンドリングヘルパー関数クラス。

    例外オブジェクトを受け取り、ユーザー向け日本語エラーメッセージ文字列を生成して返す。
    ログ出力は行わない（呼び出し元モジュールが _logger 経由でログを出力すること）。
    全メソッドは @staticmethod なので、インスタンス化不要で ErrorHandler.handle_xxx() として呼び出せる。
    """

    # ============ 共通エラーハンドリングメソッド ============

    @staticmethod
    def handle_keyboard_interrupt(e: Optional[Exception] = None) -> str:
        """キーボード中断（Ctrl+C）のユーザー向けメッセージを生成する。

        Args:
            e: 発生した例外オブジェクト（省略可）

        Returns:
            str: ユーザー向けメッセージ
        """
        return "処理を中断しました。"

    @staticmethod
    def handle_loop_limit_error(e: "LoopLimitError") -> str:
        """ループ上限到達（LoopLimitError）のユーザー向けメッセージを生成する。

        Args:
            e: LoopLimitErrorオブジェクト

        Returns:
            str: ユーザー向けエラーメッセージ
        """
        return "処理の上限に達しました。申請管理部門にお問い合わせください。"

    @staticmethod
    def handle_validation_error(e: Exception) -> str:
        """Pydanticバリデーション失敗（ValidationError）のユーザー向けメッセージを生成する。

        Args:
            e: 発生した例外オブジェクト（ValidationError）

        Returns:
            str: ユーザー向け日本語エラーメッセージ
        """
        try:
            errors = e.errors()  # type: ignore[attr-defined]
            details = "; ".join(
                f"{'.'.join(str(loc) for loc in err.get('loc', []))}: {err.get('msg', '')}"
                for err in errors
            )
            return f"入力内容に誤りがあります。{details}"
        except Exception:
            return f"入力内容に誤りがあります。{e}"

    @staticmethod
    def handle_runtime_error(e: Optional[Exception] = None) -> str:
        """その他の実行時エラー（RuntimeError）のユーザー向けメッセージを生成する。

        Args:
            e: 発生した例外オブジェクト（省略可）

        Returns:
            str: ユーザー向けエラーメッセージ
        """
        return "処理中にエラーが発生しました。申請管理部門にお問い合わせください。"

    @staticmethod
    def handle_unexpected_error(e: Optional[Exception] = None) -> str:
        """予期しないエラー（Exception）のユーザー向けメッセージを生成する。

        Args:
            e: 発生した例外オブジェクト（省略可）

        Returns:
            str: ユーザー向けエラーメッセージ
        """
        return "予期しないエラーが発生しました。申請管理部門にお問い合わせください。"

    # ============ ドメイン固有エラーハンドリングメソッド ============

    @staticmethod
    def handle_throttling_error(e: Optional[Exception] = None) -> str:
        """APIレート制限（ModelThrottledException）のユーザー向けメッセージを生成する。

        Args:
            e: 発生した例外オブジェクト（省略可）

        Returns:
            str: ユーザー向けメッセージ
        """
        return (
            "システムが混雑しています。しばらく時間をおいて再度お試しください。"
            "問題が解決しない場合は申請管理部門にお問い合わせください。"
        )

    @staticmethod
    def handle_max_tokens_error(e: Optional[Exception] = None) -> str:
        """最大トークン数到達（MaxTokensReachedException）のユーザー向けメッセージを生成する。

        Args:
            e: 発生した例外オブジェクト（省略可）

        Returns:
            str: ユーザー向けメッセージ
        """
        return "処理できる情報量の上限に達しました。入力内容を短くして再度お試しください。"

    @staticmethod
    def handle_context_window_error(e: Optional[Exception] = None) -> str:
        """コンテキストウィンドウ超過（ContextWindowOverflowException）のユーザー向けメッセージを生成する。

        Args:
            e: 発生した例外オブジェクト（省略可）

        Returns:
            str: ユーザー向けメッセージ
        """
        return "会話履歴が長くなりすぎました。新しいセッションで再度お試しください。"

    @staticmethod
    def handle_fare_data_error(e: Optional[Exception] = None) -> str:
        """運賃データ読み込み失敗（FileNotFoundError / Exception）のユーザー向けメッセージを生成する。

        Args:
            e: 発生した例外オブジェクト（省略可）

        Returns:
            str: ユーザー向けメッセージ
        """
        if isinstance(e, FileNotFoundError):
            return "運賃データが見つかりませんでした。申請管理部門にお問い合わせください。"
        return "運賃データの読み込みに失敗しました。申請管理部門にお問い合わせください。"

    @staticmethod
    def handle_calculation_error(e: Optional[Exception] = None) -> str:
        """運賃計算失敗（Exception）のユーザー向けメッセージを生成する。

        Args:
            e: 発生した例外オブジェクト（省略可）

        Returns:
            str: ユーザー向けメッセージ
        """
        return "運賃計算中にエラーが発生しました。申請管理部門にお問い合わせください。"

    @staticmethod
    def handle_file_save_error(e: Optional[Exception] = None) -> str:
        """Excelファイル保存失敗（IOError / PermissionError / Exception）のユーザー向けメッセージを生成する。

        Args:
            e: 発生した例外オブジェクト（省略可）

        Returns:
            str: ユーザー向けメッセージ
        """
        if isinstance(e, PermissionError):
            return "申請書ファイルの保存に失敗しました（権限エラー）。申請管理部門にお問い合わせください。"
        if isinstance(e, IOError):
            return "申請書ファイルの保存に失敗しました。申請管理部門にお問い合わせください。"
        return "申請書生成中にエラーが発生しました。申請管理部門にお問い合わせください。"
