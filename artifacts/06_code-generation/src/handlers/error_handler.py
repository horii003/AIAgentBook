"""エラーハンドリング・メッセージ生成

全エージェント・全ツールで共通して使用するエラーハンドリングユーティリティ。
全メソッドが @staticmethod であり、インスタンス化不要。
ログ出力は行わない（呼び出し元の責務）。
"""


class LoopLimitError(Exception):
    """ReActループ制限到達例外"""

    def __init__(
        self, current_iteration: int, max_iterations: int, agent_name: str = ""
    ):
        self.current_iteration = current_iteration
        self.max_iterations = max_iterations
        self.agent_name = agent_name
        super().__init__(
            f"ループ制限到達: agent={agent_name}, "
            f"iteration={current_iteration}/{max_iterations}"
        )


class ErrorHandler:
    """エラーメッセージ生成ユーティリティ（全メソッド @staticmethod）"""

    @staticmethod
    def handle_throttling_error(e: Exception) -> str:
        """APIレート制限エラーメッセージを生成する"""
        return "APIの利用制限に達しました。しばらく待ってから再度お試しください。"

    @staticmethod
    def handle_max_tokens_error(e: Exception) -> str:
        """最大トークン数到達メッセージを生成する"""
        return "応答が長すぎるため処理を中断しました。入力内容を短くして再度お試しください。"

    @staticmethod
    def handle_context_window_error(e: Exception) -> str:
        """コンテキストウィンドウ超過メッセージを生成する"""
        return "会話が長くなりすぎたため処理を中断しました。お手数ですが、最初からやり直してください。"

    @staticmethod
    def handle_fare_data_error(e: Exception) -> str:
        """運賃データ読み込み失敗メッセージを生成する"""
        return "運賃データの読み込みに失敗しました。担当者にお問い合わせください。"

    @staticmethod
    def handle_calculation_error(e: Exception) -> str:
        """運賃計算失敗メッセージを生成する"""
        return "交通費の計算に失敗しました。担当者にお問い合わせください。"

    @staticmethod
    def handle_file_save_error(e: Exception) -> str:
        """ファイル保存失敗メッセージを生成する"""
        return "ファイルの保存に失敗しました。担当者にお問い合わせください。"

    @staticmethod
    def handle_validation_error(e: Exception) -> str:
        """バリデーションエラーメッセージを生成する"""
        try:
            errors = e.errors()  # type: ignore[union-attr]
            if not errors:
                return "入力内容にエラーがあります。入力を確認してください。"
            messages = []
            for err in errors:
                field = ".".join(str(loc) for loc in err.get("loc", []))
                msg = err.get("msg", "不正な値です")
                messages.append(f"{field}のエラー: {msg}")
            return "入力内容にエラーがあります。" + "、".join(messages)
        except Exception:
            return "入力内容にエラーがあります。入力を確認してください。"

    @staticmethod
    def handle_keyboard_interrupt(e: Exception) -> str:
        """ユーザー中断メッセージを生成する"""
        return "処理を中断しました。"

    @staticmethod
    def handle_loop_limit_error(e: Exception) -> str:
        """ループ制限到達メッセージを生成する"""
        return "処理の上限回数に達したため、申請処理を終了します。お手数ですが、最初からやり直してください。"

    @staticmethod
    def handle_runtime_error(e: Exception) -> str:
        """実行時エラーメッセージを生成する"""
        return "処理中にエラーが発生しました。担当者にお問い合わせください。"

    @staticmethod
    def handle_unexpected_error(e: Exception) -> str:
        """予期しないエラーメッセージを生成する"""
        return "予期しないエラーが発生しました。担当者にお問い合わせください。"
