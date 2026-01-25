"""エラーハンドリング関連のモジュール"""
import logging
from datetime import datetime
from typing import Optional


class ErrorHandler:
    """エラーハンドラー"""
    
    def __init__(self, log_file: str = "logs/error.log", log_level : str = "ERROR"):
        """
        エラーハンドラーの初期化
        
        Args:
            log_file: ログファイルのパス
        """
        self.log_file = log_file
        self.log_level = log_level
        self._setup_logger()
    
    def _setup_logger(self):
        """ロガーのセットアップ"""
        import os
        
        # ログディレクトリの作成
        log_dir = os.path.dirname(self.log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # ロガーの設定
        # self.logger = logging.getLogger("TravelExpenseAgent")
        self.logger = logging.getLogger()
        self.logger.setLevel(self.log_level)

        # コンソール出力
        console_handler = logging.StreamHandler()

        # ファイルハンドラーの追加
        file_handler = logging.FileHandler(self.log_file, encoding="utf-8")
        # file_handler.setLevel(logging.INFO)
        
        # フォーマッターの設定
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s - %(message)s')
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        
        # ハンドラーの追加
        if not self.logger.handlers:
            self.logger.addHandler(console_handler)
            self.logger.addHandler(file_handler)
    
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
1. AWS認証情報が正しく設定されているか（aws configure）
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
        error_message = f"運賃データの読み込みに失敗しました: {str(error)}"
        self.log_error("FareDataLoadError", error_message, context)
        
        if "FileNotFoundError" in str(type(error)):
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
        self.log_error("ValidationError", error_message, context)
        
        user_message = f"""
入力データに問題があります。
エラー詳細: {str(error)}

正しい形式で再度入力してください。
"""
        return user_message.strip()
    
    def log_error(self, error_type: str, message: str, context: Optional[dict] = None):
        """
        エラーをログに記録
        
        Args:
            error_type: エラータイプ
            message: エラーメッセージ
            context: エラーコンテキスト
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "error_type": error_type,
            "message": message,
            "context": context or {}
        }
        
        self.logger.error(f"{error_type}: {message} | Context: {context}")
    
    def log_info(self, message: str):
        """
        情報ログの記録
        
        Args:
            message: ログメッセージ
        """
        self.logger.info(message)
