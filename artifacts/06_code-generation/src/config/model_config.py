"""LLMモデル設定

Amazon Bedrockモデルの設定を一元管理する。
"""

import os
from functools import lru_cache

from strands.models.bedrock import BedrockModel


class ModelConfig:
    """LLMモデル設定クラス"""

    DEFAULT_MODEL_ID = "jp.anthropic.claude-sonnet-4-5-20250929-v1:0"
    GUARDRAIL_ID = os.getenv("GUARDRAIL_ID", "")
    GUARDRAIL_VERSION = os.getenv("GUARDRAIL_VERSION", "DRAFT")

    @classmethod
    @lru_cache(maxsize=1)
    def get_model(cls) -> BedrockModel:
        """BedrockModelインスタンスを取得する（キャッシュ付き）"""
        return BedrockModel(
            model_id=cls.DEFAULT_MODEL_ID,
            guardrail_id=cls.GUARDRAIL_ID,
            guardrail_version=cls.GUARDRAIL_VERSION,
            guardrail_trace="enabled",
        )
