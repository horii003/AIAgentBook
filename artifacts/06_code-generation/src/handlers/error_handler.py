"""エラーハンドリング関連のモジュール"""
from typing import Optional


class LoopLimitError(Exception):
    """ReActループ上限到達時に発生するカスタム例外。

    Attributes:
        current_iteration: 現在のループ回数
        max_iterations: ループ上限回数
        agent_name: エージェント名
    """

    def __init__(self, current_iteration: int, max_iterations: int, agent_name: str):
        """初期化

        Args:
            current_iteration: 現在のループ回数
            max_iterations: 最大ループ回数
            agent_name: エージェント名
        """
        self.current_iteration = current_iteration
        self.max_iterations = max_iterations
        self.agent_name = agent_name
        super().__init__(
            f"ループ上限（{max_iterations}回）に達しました: agent={agent_name}, iteration={current_iteration}"
        )


class ErrorHandler:
    """エラーハンドリングヘルパー関数クラス

    例外オブジェクトを受け取り、ユーザー向け日本語エラーメッセージ文字列を生成して返す。
    ログ出力は行わない（呼び出し元モジュールが _logger 経由でログを出力すること）。
    全メソッドは @staticmethod なので、インスタンス化不要で ErrorHandler.handle_xxx() として呼び出せる。
    """

    @staticmethod
    def handle_keyboard_interrupt(error: Optional[Exception] = None) -> str:
        """キーボード中断（Ctrl+C）の処理

        Args:
            error: 発生した例外オブジェクト（省略可）

        Returns:
            str: ユーザー向けメッセージ
        """
        return "処理を中断しました。ご利用ありがとうございました。"

    @staticmethod
    def handle_loop_limit_error(error: "LoopLimitError") -> str:
        """ループ上限到達エラーの処理

        Args:
            error: LoopLimitErrorオブジェクト

        Returns:
            str: ユーザー向けエラーメッセージ
        """
        return "申し訳ありません。処理の上限回数に達したため、申請処理を中断しました。お手数ですが、最初からやり直してください。問題が続く場合はシステム管理者にご連絡ください。"

    @staticmethod
    def handle_validation_error(error: Exception) -> str:
        """Pydantic ValidationErrorの処理

        Args:
            error: 発生した例外オブジェクト（ValidationError）

        Returns:
            str: ユーザー向け日本語エラーメッセージ
        """
        try:
            errors = error.errors()
            messages = []
            for e in errors:
                loc = ".".join(str(l) for l in e.get("loc", []))
                msg = e.get("msg", "")
                messages.append(f"{loc}のエラー: {msg}")
            return "入力内容にエラーがあります。" + " ".join(messages)
        except Exception:
            return "入力内容にエラーがあります。入力値を確認してください。"

    @staticmethod
    def handle_runtime_error(error: Optional[Exception] = None) -> str:
        """RuntimeErrorの処理

        Args:
            error: 発生した例外オブジェクト（省略可）

        Returns:
            str: ユーザー向けエラーメッセージ
        """
        return "申し訳ありません。実行時エラーが発生しました。システム管理者にご連絡ください。"

    @staticmethod
    def handle_unexpected_error(error: Optional[Exception] = None) -> str:
        """予期しないエラーの処理

        Args:
            error: 発生した例外オブジェクト（省略可）

        Returns:
            str: ユーザー向けエラーメッセージ
        """
        return "申し訳ありません。予期しないエラーが発生しました。システム管理者にご連絡ください。"

    @staticmethod
    def handle_throttling_error(error: Optional[Exception] = None) -> str:
        """APIレート制限エラーの処理

        Args:
            error: 発生した例外オブジェクト（省略可）

        Returns:
            str: ユーザー向けエラーメッセージ
        """
        return "申し訳ありません。現在アクセスが集中しています。しばらく待ってから再度お試しください。"

    @staticmethod
    def handle_max_tokens_error(error: Optional[Exception] = None) -> str:
        """最大トークン数到達エラーの処理

        Args:
            error: 発生した例外オブジェクト（省略可）

        Returns:
            str: ユーザー向けエラーメッセージ
        """
        return "申し訳ありません。処理できる情報量の上限に達しました。入力内容を短くして再度お試しください。"

    @staticmethod
    def handle_context_window_error(error: Optional[Exception] = None) -> str:
        """コンテキストウィンドウ超過エラーの処理

        Args:
            error: 発生した例外オブジェクト（省略可）

        Returns:
            str: ユーザー向けエラーメッセージ
        """
        return "申し訳ありません。会話の履歴が長くなりすぎました。最初からやり直してください。"

    @staticmethod
    def handle_fare_data_error(error: Optional[Exception] = None) -> str:
        """運賃データ読み込み失敗の処理

        Args:
            error: 発生した例外オブジェクト（省略可）

        Returns:
            str: ユーザー向けエラーメッセージ
        """
        return "申し訳ありません。運賃データの読み込みに失敗しました。システム管理者にご連絡ください。"

    @staticmethod
    def handle_calculation_error(error: Optional[Exception] = None) -> str:
        """運賃計算失敗の処理

        Args:
            error: 発生した例外オブジェクト（省略可）

        Returns:
            str: ユーザー向けエラーメッセージ
        """
        return "申し訳ありません。交通費の計算中にエラーが発生しました。システム管理者にご連絡ください。"

    @staticmethod
    def handle_file_save_error(error: Optional[Exception] = None) -> str:
        """Excelファイル保存失敗の処理

        Args:
            error: 発生した例外オブジェクト（省略可）

        Returns:
            str: ユーザー向けエラーメッセージ
        """
        return "申し訳ありません。申請書の保存に失敗しました。システム管理者にご連絡ください。"
