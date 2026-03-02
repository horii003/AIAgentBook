"""エラーハンドリング関連のモジュール"""
import logging

logger = logging.getLogger(__name__)


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
        
        message = (
            f"エージェント '{agent_name}' のループ制限に到達しました "
            f"({current_iteration}/{max_iterations}回)"
        )
        super().__init__(message)


class ErrorHandler:
    """ユーザー向けエラーメッセージ生成クラス"""

    def handle_throttling_error(self, error: Exception) -> str:
        """
        APIレート制限エラーの処理

        Args:
            error: ModelThrottledExceptionオブジェクト

        Returns:
            str: ユーザー向けエラーメッセージ
        """
        user_message = """
        Amazon Bedrockへのリクエストが集中しています。
        しばらく時間をおいてから再度お試しください。
        
        問題が解決しない場合は、システム管理者にお問い合わせください。
        """
        return user_message.strip()


    def handle_max_tokens_error(self, error: Exception) -> str:
        """
        最大トークン数到達エラーの処理

        Args:
            error: MaxTokensReachedExceptionオブジェクト

        Returns:
            str: ユーザー向けエラーメッセージ
        """
        user_message = """
        処理できる文章量の上限に達しました。
        システムを再起動して、最初からお試しください。
        
        申請内容が長い場合は、複数回に分けて申請してください。
        """
        return user_message.strip()


    def handle_context_window_error(self, error: Exception) -> str:
        """
        コンテキストウィンドウ超過エラーの処理

        Args:
            error: ContextWindowOverflowExceptionオブジェクト

        Returns:
            str: ユーザー向けエラーメッセージ
        """
        user_message = """
        会話の内容が長くなりすぎて処理できなくなりました。
        システムを再起動して、最初からお試しください。
        
        申請内容が複雑な場合は、1件ずつ分けて申請してください。
        """
        return user_message.strip()


    def handle_fare_data_error(self, error: Exception) -> str:
        """
        運賃データ読み込みエラーの処理
        
        Args:
            error: エラーオブジェクト
        
        Returns:
            str: ユーザー向けエラーメッセージ
        """
        if isinstance(error, FileNotFoundError):
            user_message = """
            運賃データファイルが見つかりません。
            dataフォルダに以下のファイルが存在することを確認してください：
            - train_fares.json（電車運賃データ）
            - fixed_fares.json（バス、タクシー、飛行機の固定運賃）

            交通費を計算できないため、システムを終了してください。
            """
        else:
            user_message = f"""
            運賃データの読み込み中にエラーが発生しました。
            エラー詳細: {str(error)}
            データファイルの形式が正しいか確認してください。
            交通費を計算できないため、システムを終了してください。
            """

        return user_message.strip()


    def handle_calculation_error(self, error: Exception) -> str:
        """
        計算エラーの処理
        
        Args:
            error: エラーオブジェクト
        
        Returns:
            str: ユーザー向けエラーメッセージ
        """
        user_message = f"""
                交通費の計算中にエラーが発生しました。
                エラー詳細: {str(error)}

                以下をお試しください：
                1. 出発地と目的地が正しいか確認
                2. 交通手段が正しいか確認（train/bus/taxi/airplane）
                3. 手動で金額を入力

                もう一度入力してください。
                """
        return user_message.strip()


    def handle_file_save_error(self, error: Exception) -> str:
        """
        ファイル保存エラーの処理
        
        Args:
            error: エラーオブジェクト
        
        Returns:
            str: ユーザー向けエラーメッセージ
        """
        user_message = f"""
        申請書の保存中にエラーが発生しました。
        エラー詳細: {str(error)}
        
        以下を確認してください：
        1. outputフォルダへの書き込み権限があるか
        2. ディスク容量が十分にあるか
        
        代替の保存場所を指定する場合は、システム管理者にお問い合わせください。
        """
        return user_message.strip()


    def handle_validation_error(self, error: Exception) -> str:
        """
        入力検証エラーの処理
        
        Args:
            error: エラーオブジェクト
        
        Returns:
            str: ユーザー向けエラーメッセージ
        """
        user_message = f"""
        入力データに問題があります。
        エラー詳細: {str(error)}
        正しい形式で再度入力してください。
        """
        return user_message.strip()


    def handle_keyboard_interrupt(self) -> str:
        """
        キーボード中断（Ctrl+C）の処理
        
        Returns:
            str: ユーザー向けメッセージ
        """
        return "ユーザーによる中断により、システムを終了します。"


    def handle_loop_limit_error(self, error: LoopLimitError) -> str:
        """
        エージェントループ制限エラーの処理
        
        Args:
            error: LoopLimitErrorオブジェクト
        
        Returns:
            str: 構造化されたエラーレスポンス
        """
        error_message = f"エージェント '{error.agent_name}' がループ制限に到達: {error.current_iteration}/{error.max_iterations}"
        
        if "交通費" in error.agent_name:
            specific_example = "複数の経路を一度に申請する場合は、1経路ずつ申請してください"
        elif "経費精算" in error.agent_name or "領収書" in error.agent_name:
            specific_example = "複数の領収書を一度に申請する場合は、1枚ずつ申請してください"
        else:
            specific_example = "複数の申請を一度に行う場合は、1つずつ申請してください"
        
        user_message = f"""
        申し訳ございません。処理が複雑すぎて完了できませんでした。
        エージェントループが発生しているようです。
        
        以下のいずれかをお試しください：
        1. タスクをより小さな単位に分割してください
        例：{specific_example}
        
        2. より具体的な指示を提供してください
        例：「交通費を申請したい」→「2024年1月10日の東京から大阪への新幹線代を申請したい」
        
        3. 不要な情報を削除してください
        例：申請に関係のない質問や情報は別途お尋ねください

        シンプルな内容で再度お試しください。
        """
        return user_message.strip()


    def handle_runtime_error(self, error: Exception) -> str:
        """
        RuntimeErrorの処理
        
        Args:
            error: エラーオブジェクト
        
        Returns:
            str: ユーザー向けエラーメッセージ
        """
        user_message = """
        【エラー】
        申し訳ございません。処理中にエラーが発生しました。
        システムを再起動してください。
        また、問題が解決しない場合は、システム管理者にお問い合わせください
        """
        return user_message.strip()


    def handle_unexpected_error(self, error: Exception) -> str:
        """
        予期しないエラーの処理
        
        Args:
            error: エラーオブジェクト
        
        Returns:
            str: ユーザー向けエラーメッセージ
        """
        user_message = """
        【予期しないエラー】
        申し訳ございません。予期しないエラーが発生しました。
        システムを再起動してください。
        また、問題が解決しない場合は、システム管理者に伝えてください
        """
        return user_message.strip()
