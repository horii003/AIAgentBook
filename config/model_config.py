"""Bedrockモデル設定

このファイルでは、各エージェントが使用するBedrockモデルの設定を定義します。
モデルやパラメータを変更する場合は、このファイルを編集してください。
"""
from strands.models import BedrockModel


class ModelConfig:
    """Bedrockモデル設定クラス"""
    
    # モデルID
    DEFAULT_MODEL_ID = "jp.anthropic.claude-sonnet-4-5-20250929-v1:0"
    
    @classmethod
    def get_model(cls) -> BedrockModel:
        """
        BedrockModelインスタンスを取得
        
        Returns:
            BedrockModel: 設定済みのBedrockModelインスタンス
        """
        return BedrockModel(
            model_id=cls.DEFAULT_MODEL_ID,
        )
