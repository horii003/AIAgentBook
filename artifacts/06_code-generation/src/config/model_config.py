"""Bedrockモデル設定

各エージェントが使用するBedrockモデルの設定を一元管理する。
モデルIDやガードレール設定はこのファイルで変更する。
"""
import os
from functools import lru_cache

from strands.models import BedrockModel


class ModelConfig:
    """Bedrockモデル設定クラス。

    全エージェントで共通のBedrockモデル設定を提供する。
    get_model()はlru_cacheにより同一インスタンスを返す。
    """

    # モデルID（日本リージョン: jp.anthropic.claude-sonnet-4-5-20250929-v1:0）
    DEFAULT_MODEL_ID = "jp.anthropic.claude-sonnet-4-5-20250929-v1:0"

    # ガードレール設定（Amazon Bedrockで作成したガードレールIDを環境変数から取得）
    GUARDRAIL_ID = os.getenv("GUARDRAIL_ID", "")
    GUARDRAIL_VERSION = os.getenv("GUARDRAIL_VERSION", "DRAFT")

    @classmethod
    @lru_cache(maxsize=1)
    def get_model(cls) -> BedrockModel:
        """BedrockModelインスタンスを取得する。

        lru_cacheにより同一インスタンスを返す（シングルトン相当）。

        Returns:
            BedrockModel: 設定済みのBedrockModelインスタンス
        """
        return BedrockModel(
            model_id=cls.DEFAULT_MODEL_ID,
            guardrail_id=cls.GUARDRAIL_ID if cls.GUARDRAIL_ID else None,
            guardrail_version=cls.GUARDRAIL_VERSION,
            guardrail_trace="enabled",
        )
