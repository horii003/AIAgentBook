"""Bedrockモデル設定

各エージェントが使用するBedrockモデルの設定を一元管理する。
"""
import os
from functools import lru_cache
from strands.models import BedrockModel


class ModelConfig:
    """Bedrockモデル設定クラス"""

    DEFAULT_MODEL_ID = "jp.anthropic.claude-sonnet-4-5-20250929-v1:0"
    GUARDRAIL_ID = os.getenv("GUARDRAIL_ID")
    GUARDRAIL_VERSION = "DRAFT"

    @classmethod
    @lru_cache(maxsize=1)
    def get_model(cls) -> BedrockModel:
        """BedrockModelインスタンスを取得する。

        Returns:
            BedrockModel: 設定済みのBedrockModelインスタンス
        """
        return BedrockModel(
            model_id=cls.DEFAULT_MODEL_ID,
            guardrail_id=cls.GUARDRAIL_ID,
            guardrail_version=cls.GUARDRAIL_VERSION,
            guardrail_trace="enabled",
        )
