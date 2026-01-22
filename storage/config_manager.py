"""
設定管理モジュール

アプリケーションの設定を管理するConfigManagerクラスを提供します。
環境変数からの設定読み込み、設定の更新、妥当性検証を行います。
"""

import os
import logging
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

# .envファイルを読み込み
load_dotenv()

logger = logging.getLogger(__name__)


class ConfigManager:
    """
    設定管理クラス
    
    アプリケーションの設定を管理します。
    環境変数から初期設定を読み込み、実行時に設定を更新できます。
    
    Attributes:
        applicant_name: 申請者名
        output_directory: 出力ディレクトリのパス
        bedrock_token: Bedrock認証トークン
        aws_access_key_id: AWS アクセスキーID
        aws_secret_access_key: AWS シークレットアクセスキー
        aws_region: AWS リージョン
    """
    
    def __init__(self):
        """設定の初期化"""
        # 環境変数から設定を読み込み
        self.applicant_name = os.getenv("APPLICANT_NAME", "未設定")
        self.output_directory = os.getenv("OUTPUT_DIRECTORY", "./output")
        self.bedrock_token = os.getenv("AWS_BEARER_TOKEN_BEDROCK")
        self.aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.aws_region = os.getenv("AWS_DEFAULT_REGION", "ap-northeast-1")
        
        # 出力ディレクトリの作成
        Path(self.output_directory).mkdir(parents=True, exist_ok=True)
        
        logger.info(f"設定を初期化しました: 申請者名={self.applicant_name}, 出力先={self.output_directory}")
    
    def get_applicant_name(self) -> str:
        """
        申請者名を取得
        
        Returns:
            str: 申請者名
        """
        return self.applicant_name
    
    def set_applicant_name(self, name: str) -> None:
        """
        申請者名を設定
        
        Args:
            name: 申請者名
        """
        self.applicant_name = name
        logger.info(f"申請者名を更新しました: {name}")
    
    def get_output_directory(self) -> str:
        """
        出力ディレクトリを取得
        
        Returns:
            str: 出力ディレクトリのパス
        """
        return self.output_directory
    
    def set_output_directory(self, directory: str) -> None:
        """
        出力ディレクトリを設定
        
        Args:
            directory: 出力ディレクトリのパス
        """
        self.output_directory = directory
        # ディレクトリの作成
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"出力ディレクトリを更新しました: {directory}")
    
    def get_bedrock_token(self) -> Optional[str]:
        """
        Bedrock認証トークンを取得
        
        Returns:
            Optional[str]: Bedrock認証トークン（設定されていない場合はNone）
        """
        return self.bedrock_token
    
    def get_aws_credentials(self) -> dict:
        """
        AWS認証情報を取得
        
        Returns:
            dict: AWS認証情報（access_key_id, secret_access_key, region）
        """
        return {
            "access_key_id": self.aws_access_key_id,
            "secret_access_key": self.aws_secret_access_key,
            "region": self.aws_region
        }
    
    def validate(self) -> bool:
        """
        設定の妥当性を検証
        
        必須の設定が欠落していないかチェックします。
        
        Returns:
            bool: 設定が妥当な場合True、そうでない場合False
            
        Raises:
            ValueError: 必須の設定が欠落している場合
        """
        errors = []
        
        # Bedrock認証情報のチェック（トークンまたはAWSキーのいずれかが必要）
        if not self.bedrock_token and not (self.aws_access_key_id and self.aws_secret_access_key):
            errors.append("Bedrock認証情報が設定されていません。AWS_BEARER_TOKEN_BEDROCKまたはAWS認証情報を設定してください。")
        
        # 申請者名のチェック
        if self.applicant_name == "未設定":
            logger.warning("申請者名が設定されていません。デフォルト値「未設定」を使用します。")
        
        # 出力ディレクトリのチェック
        if not self.output_directory:
            errors.append("出力ディレクトリが設定されていません。")
        
        if errors:
            error_message = "\n".join(errors)
            logger.error(f"設定の検証に失敗しました:\n{error_message}")
            raise ValueError(f"設定エラー:\n{error_message}")
        
        logger.info("設定の検証に成功しました")
        return True
