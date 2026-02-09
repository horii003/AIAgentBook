"""エラーハンドリング関連のモジュール"""
import logging
from datetime import datetime
from typing import Optional


class ErrorHandler:
    """エラーハンドリング + ログ出力ヘルパー関数クラス"""
    
    def __init__(self):
        """
        エラーハンドラーの初期化
        
        Note:
            ログ設定はmain.pyで実施済み
        """

        self.logger = logging.getLogger(__name__)


    def log_info(self, message: str, context: Optional[dict] = None):
        """
        情報ログを出力
        
        Args:
            message: ログメッセージ
            context: コンテキスト情報（オプション）
        """
        if context:
            self.logger.info(f"{message} | Context: {context}")
        else:
            self.logger.info(message)
    

    def log_error(self, error_type: str, message: str, context: Optional[dict] = None, exc_info: bool = False):
        """
        エラーログを出力
        
        Args:
            error_type: エラータイプ
            message: エラーメッセージ
            context: エラーコンテキスト（オプション）
            exc_info: スタックトレースをログに含めるか
        """
        if exc_info:
            self.logger.error(f"{error_type}: {message} | Context: {context}", exc_info=True)
        else:
            self.logger.error(f"{error_type}: {message} | Context: {context}")
    


#別途エラーハンドリングを定義 ==========

    def handle_bedrock_error(self, error: Exception, context: Optional[dict] = None) -> str:
        """
        Bedrock接続エラーの処理
        
        Args:
            error: エラーオブジェクト
            context: エラーコンテキスト
        
        Returns:
            str: ユーザー向けエラーメッセージ
        """
        error_message = f"Amazon Bedrockサービスへの接続に失敗しました: {str(error)}"
        self.log_error("BedrockConnectionError", error_message, context)
        
        user_message = """
        Amazon Bedrockサービスに接続できませんでした。
        以下を確認してください：
        1. AWS認証情報が正しく設定されているか
        2. インターネット接続が正常か
        3. Amazon Bedrockへのアクセス権限があるか
        
        問題が解決しない場合は、システム管理者にお問い合わせください。
        """
        
        return user_message.strip()
    

    def handle_fare_data_error(self, error: Exception, context: Optional[dict] = None) -> str:
        """
        運賃データ読み込みエラーの処理
        
        Args:
            error: エラーオブジェクト
            context: エラーコンテキスト
        
        Returns:
            str: ユーザー向けエラーメッセージ
        """
        # ログ出力
        self.log_error("FareDataLoadError", str(error), context)
        
        # メッセージ生成
        if isinstance(error, FileNotFoundError):
            user_message = """
            運賃データファイルが見つかりません。
            dataフォルダに以下のファイルが存在することを確認してください：
            - train_fares.json（電車運賃データ）
            - fixed_fares.json（バス、タクシー、飛行機の固定運賃）

            システムを終了します。
            """
        else:
            user_message = f"""
            運賃データの読み込み中にエラーが発生しました。
            エラー詳細: {str(error)}
            データファイルの形式が正しいか確認してください。
            システムを終了します。
            """

        return user_message.strip()


    def handle_calculation_error(self, error: Exception, context: Optional[dict] = None) -> str:
        """
        計算エラーの処理
        
        Args:
            error: エラーオブジェクト
            context: エラーコンテキスト
        
        Returns:
            str: ユーザー向けエラーメッセージ
        """
        error_message = f"交通費の計算に失敗しました: {str(error)}"
        self.log_error("CalculationError", error_message, context)
        
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
    

    def handle_file_save_error(self, error: Exception, context: Optional[dict] = None) -> str:
        """
        ファイル保存エラーの処理
        
        Args:
            error: エラーオブジェクト
            context: エラーコンテキスト
        
        Returns:
            str: ユーザー向けエラーメッセージ
        """
        error_message = f"ファイルの保存に失敗しました: {str(error)}"
        self.log_error("FileSaveError", error_message, context)
        
        user_message = f"""
        申請書の保存中にエラーが発生しました。
        エラー詳細: {str(error)}
        
        以下を確認してください：
        1. outputフォルダへの書き込み権限があるか
        2. ディスク容量が十分にあるか
        
        代替の保存場所を指定する場合は、システム管理者にお問い合わせください。
        
        """

        return user_message.strip()
    

    def handle_validation_error(self, error: Exception, context: Optional[dict] = None) -> str:
        """
        入力検証エラーの処理
        
        Args:
            error: エラーオブジェクト
            context: エラーコンテキスト
        
        Returns:
            str: ユーザー向けエラーメッセージ
        """
        error_message = f"入力データの検証に失敗しました: {str(error)}"
        
        #ログ出力
        self.log_error("ValidationError", error_message, context)
        
        #ユーザー向けメッセージ作成
        user_message = f"""
        入力データに問題があります。
        エラー詳細: {str(error)}
        正しい形式で再度入力してください。
        """

        return user_message.strip()
    
    
    def handle_loop_limit_error(self, error: Exception, context: Optional[dict] = None) -> str:
        """
        エージェントループ制限エラーの処理
        
        Args:
            error: エラーオブジェクト
            context: エラーコンテキスト
        
        Returns:
            str: ユーザー向けエラーメッセージ
        """
        error_message = f"エージェントループの制限に到達しました: {str(error)}"
        self.log_error("LoopLimitError", error_message, context)
        
        user_message = """
        申し訳ございません。処理が複雑すぎて完了できませんでした。
        
        以下のいずれかをお試しください：
        1. タスクをより小さな単位に分割してください
        例：複数の申請を一度に行う場合は、1つずつ申請してください
        
        2. より具体的な指示を提供してください
        例：「交通費を申請したい」→「2024年1月10日の東京から大阪への新幹線代を申請したい」
        
        3. 不要な情報を削除してください
        例：申請に関係のない質問や情報は別途お尋ねください
        
        もう一度、シンプルな内容でお試しください。
        """
        
        return user_message.strip()
    
