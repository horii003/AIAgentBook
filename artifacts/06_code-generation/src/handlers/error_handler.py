"""エラーハンドリング関連のモジュール

全エージェント・全ツールで共通して使用するエラーハンドリングユーティリティ。
ログ出力は行わない（呼び出し元モジュールが行う）。
"""
from typing import Optional


class LoopLimitError(RuntimeError):
    """エージェントReActループの制限エラー

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
            f"{agent_name} のループ回数が上限（{max_iterations}回）に達しました。"
            f"（現在: {current_iteration}回）"
        )
        super().__init__(message)


class ErrorHandler:
    """エラーハンドリングヘルパー関数クラス

    例外オブジェクトを受け取り、ユーザー向け日本語エラーメッセージ文字列を生成して返す。
    ログ出力は行わない（呼び出し元モジュールが _logger 経由でログを出力すること）。
    全メソッドは @staticmethod なので、インスタンス化不要で ErrorHandler.handle_xxx() として呼び出せる。
    """

    @staticmethod
    def handle_throttling_error(e: Exception) -> str:
        """APIレート制限エラーのユーザー向けメッセージを生成する。

        Args:
            e: APIレート制限例外インスタンス

        Returns:
            str: ユーザー向けエラーメッセージ
        """
        return "APIのリクエスト制限に達しました。しばらく待ってから再度お試しください。"

    @staticmethod
    def handle_max_tokens_error(e: Exception) -> str:
        """最大トークン数到達時のユーザー向けメッセージを生成する。

        Args:
            e: 最大トークン数到達例外インスタンス

        Returns:
            str: ユーザー向けエラーメッセージ
        """
        return "処理できる情報量の上限に達しました。入力内容を短くして再度お試しください。"

    @staticmethod
    def handle_context_window_error(e: Exception) -> str:
        """コンテキストウィンドウ超過時のユーザー向けメッセージを生成する。

        Args:
            e: コンテキストウィンドウ超過例外インスタンス

        Returns:
            str: ユーザー向けエラーメッセージ
        """
        return "会話履歴が長くなりすぎました。会話をリセットして最初からお試しください。"

    @staticmethod
    def handle_fare_data_error(e: Exception) -> str:
        """運賃データ読み込み失敗時のユーザー向けメッセージを生成する。

        Args:
            e: 運賃データ読み込み例外インスタンス

        Returns:
            str: ユーザー向けエラーメッセージ
        """
        return "運賃データの読み込みに失敗しました。システム管理者にお問い合わせください。"

    @staticmethod
    def handle_calculation_error(e: Exception) -> str:
        """運賃計算失敗時のユーザー向けメッセージを生成する。

        Args:
            e: 運賃計算例外インスタンス

        Returns:
            str: ユーザー向けエラーメッセージ
        """
        return "交通費の計算に失敗しました。出発地・目的地・交通手段を確認して再度お試しください。"

    @staticmethod
    def handle_file_save_error(e: Exception) -> str:
        """Excelファイル保存失敗時のユーザー向けメッセージを生成する。

        Args:
            e: ファイル保存例外インスタンス

        Returns:
            str: ユーザー向けエラーメッセージ
        """
        return "申請書ファイルの保存に失敗しました。ディスクの空き容量やアクセス権限を確認してください。"

    @staticmethod
    def handle_validation_error(e: Exception) -> str:
        """Pydantic バリデーションエラーのユーザー向けメッセージを生成する。

        Args:
            e: ValidationError インスタンス

        Returns:
            str: ユーザー向けエラーメッセージ
        """
        try:
            errors = e.errors()
            details = []
            for err in errors:
                field = ".".join(str(loc) for loc in err.get("loc", []))
                msg = err.get("msg", "")
                details.append(f"{field}のエラー: {msg}" if field else msg)
            detail_str = "、".join(details)
            return f"入力内容にエラーがあります。{detail_str}"
        except Exception:
            return "入力内容にエラーがあります。入力値を確認して再度お試しください。"

    @staticmethod
    def handle_keyboard_interrupt(e: Optional[Exception] = None) -> str:
        """ユーザーによる中断時のユーザー向けメッセージを生成する。

        Args:
            e: キーボード割り込み例外インスタンス（省略可）

        Returns:
            str: ユーザー向けメッセージ
        """
        return "処理を中断しました。ご利用ありがとうございました。"

    @staticmethod
    def handle_loop_limit_error(e: "LoopLimitError") -> str:
        """ReActループ制限到達時のユーザー向けメッセージを生成する。

        Args:
            e: LoopLimitError インスタンス

        Returns:
            str: ユーザー向けエラーメッセージ
        """
        return (
            f"{e.agent_name} の処理回数が上限（{e.max_iterations}回）に達しました。"
            "入力内容を整理して再度お試しください。"
        )

    @staticmethod
    def handle_runtime_error(e: Optional[Exception] = None) -> str:
        """その他の実行時エラーのユーザー向けメッセージを生成する。

        Args:
            e: 実行時例外インスタンス（省略可）

        Returns:
            str: ユーザー向けエラーメッセージ
        """
        return "処理中にエラーが発生しました。再度お試しください。"

    @staticmethod
    def handle_unexpected_error(e: Optional[Exception] = None) -> str:
        """予期しないエラーのユーザー向けメッセージを生成する。

        Args:
            e: 予期しない例外インスタンス（省略可）

        Returns:
            str: ユーザー向けエラーメッセージ
        """
        return "予期しないエラーが発生しました。システム管理者にお問い合わせください。"
