"""Bedrockモデル設定

このファイルでは、各エージェントが使用するBedrockモデルの設定を定義します。
"""
import os
from functools import lru_cache
from strands.models import BedrockModel


class ModelConfig:
    """Bedrockモデル設定クラス"""

    # モデルID
    DEFAULT_MODEL_ID = "jp.anthropic.claude-sonnet-4-5-20250929-v1:0"

    # ガードレール設定（環境変数から取得）
    GUARDRAIL_ID = os.getenv("GUARDRAIL_ID")
    GUARDRAIL_VERSION = os.getenv("GUARDRAIL_VERSION", "DRAFT")

    @classmethod
    @lru_cache(maxsize=1)
    def get_model(cls) -> BedrockModel:
        """BedrockModelインスタンスを取得

        Returns:
            BedrockModel: 設定済みのBedrockModelインスタンス
        """
        return BedrockModel(
            model_id=cls.DEFAULT_MODEL_ID,
            guardrail_id=cls.GUARDRAIL_ID,
            guardrail_version=cls.GUARDRAIL_VERSION,
            guardrail_trace="enabled",
        )
