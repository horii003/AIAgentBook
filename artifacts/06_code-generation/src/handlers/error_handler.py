"""エラーハンドリング関連のモジュール"""


class LoopLimitError(Exception):
    """ReActループが最大回数に到達した際に送出される例外。"""

    def __init__(self, current_iteration: int, max_iterations: int, agent_name: str) -> None:
        """初期化する。

        Args:
            current_iteration: 現在のループ回数
            max_iterations: 最大ループ回数
            agent_name: エージェント名
        """
        self.current_iteration = current_iteration
        self.max_iterations = max_iterations
        self.agent_name = agent_name
        super().__init__(
            f"エージェント '{agent_name}' の最大ループ回数({max_iterations}回)に到達しました"
            f"（現在: {current_iteration}回）"
        )


class ErrorHandler:
    """エラーハンドリングヘルパー関数クラス

    例外オブジェクトを受け取り、ユーザー向け日本語エラーメッセージ文字列を生成して返す。
    ログ出力は行わない（呼び出し元モジュールが _logger 経由でログを出力すること）。

    全メソッドは @staticmethod なので、インスタンス化不要で ErrorHandler.handle_xxx() として呼び出せる。
    """

    @staticmethod
    def handle_throttling_error(error: Exception) -> str:
        """APIレート制限エラーのユーザー向けメッセージを生成する。

        Args:
            error: 発生した例外オブジェクト

        Returns:
            str: ユーザー向けメッセージ
        """
        return "APIのリクエスト制限に達しました。しばらく時間をおいて再度お試しください。"

    @staticmethod
    def handle_max_tokens_error(error: Exception) -> str:
        """最大トークン数到達エラーのユーザー向けメッセージを生成する。

        Args:
            error: 発生した例外オブジェクト

        Returns:
            str: ユーザー向けメッセージ
        """
        return "処理できるテキスト量の上限に達しました。入力内容を短くして再度お試しください。"

    @staticmethod
    def handle_context_window_error(error: Exception) -> str:
        """コンテキストウィンドウ超過エラーのユーザー向けメッセージを生成する。

        Args:
            error: 発生した例外オブジェクト

        Returns:
            str: ユーザー向けメッセージ
        """
        return "会話履歴が長くなりすぎました。リセットして最初からやり直してください。"

    @staticmethod
    def handle_fare_data_error(error: Exception) -> str:
        """運賃データ読み込み失敗エラーのユーザー向けメッセージを生成する。

        Args:
            error: 発生した例外オブジェクト

        Returns:
            str: ユーザー向けメッセージ
        """
        return "運賃データの読み込みに失敗しました。手動で金額を入力してください。"

    @staticmethod
    def handle_calculation_error(error: Exception) -> str:
        """運賃計算失敗エラーのユーザー向けメッセージを生成する。

        Args:
            error: 発生した例外オブジェクト

        Returns:
            str: ユーザー向けメッセージ
        """
        return "交通費の計算中にエラーが発生しました。手動で金額を入力してください。"

    @staticmethod
    def handle_file_save_error(error: Exception) -> str:
        """ファイル保存失敗エラーのユーザー向けメッセージを生成する。

        Args:
            error: 発生した例外オブジェクト

        Returns:
            str: ユーザー向けメッセージ
        """
        return f"申請書ファイルの保存に失敗しました。再度お試しください。（詳細: {error}）"

    @staticmethod
    def handle_validation_error(error: Exception) -> str:
        """バリデーションエラーのユーザー向けメッセージを生成する。

        Args:
            error: Pydantic v2のValidationErrorインスタンス

        Returns:
            str: ユーザー向け日本語エラーメッセージ
        """
        field_errors = []
        for err in error.errors():
            loc = ".".join(str(part) for part in err["loc"])
            msg = err["msg"]
            field_errors.append(f"- {loc}: {msg}")

        error_details = "\n".join(field_errors)
        return f"入力データに不備があります。以下の項目を確認してください。\n{error_details}"

    @staticmethod
    def handle_keyboard_interrupt(error: Exception) -> str:
        """キーボード中断のユーザー向けメッセージを生成する。

        Args:
            error: 発生した例外オブジェクト

        Returns:
            str: ユーザー向けメッセージ
        """
        return "操作が中断されました。"

    @staticmethod
    def handle_loop_limit_error(error: "LoopLimitError") -> str:
        """ループ制限到達エラーのユーザー向けメッセージを生成する。

        Args:
            error: LoopLimitErrorインスタンス

        Returns:
            str: ユーザー向けエラーメッセージ
        """
        return "処理がループ回数の上限に達したため完了できませんでした。入力内容を見直して再度お試しください。"

    @staticmethod
    def handle_runtime_error(error: Exception) -> str:
        """RuntimeErrorのユーザー向けメッセージを生成する。

        Args:
            error: 発生した例外オブジェクト

        Returns:
            str: ユーザー向けエラーメッセージ
        """
        return f"実行時エラーが発生しました。しばらく時間をおいて再度お試しください。（詳細: {error}）"

    @staticmethod
    def handle_unexpected_error(error: Exception) -> str:
        """予期しないエラーのユーザー向けメッセージを生成する。

        Args:
            error: 予期しない例外インスタンス

        Returns:
            str: ユーザー向けエラーメッセージ
        """
        error_type = type(error).__name__
        return f"予期しないエラーが発生しました。しばらく時間をおいて再度お試しください。（エラー種別: {error_type}）"
