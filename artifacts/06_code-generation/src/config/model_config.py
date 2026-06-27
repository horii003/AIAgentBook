"""Bedrockモデル設定

このファイルでは、各エージェントが使用するBedrockモデルの設定を定義します。
モデルやパラメータを変更する場合は、このファイルを編集してください。
"""
import logging
import os
from functools import lru_cache

from strands.models import BedrockModel

_logger = logging.getLogger(__name__)


class ModelConfig:
    """Bedrockモデル設定クラス"""

    # モデルID
    DEFAULT_MODEL_ID = "jp.anthropic.claude-sonnet-4-5-20250929-v1:0"

    @classmethod
    @lru_cache(maxsize=1)
    def get_model(cls) -> BedrockModel:
        """BedrockModelインスタンスを取得する。

        Returns:
            BedrockModel: 設定済みのBedrockModelインスタンス
        """
        guardrail_id = os.getenv("GUARDRAIL_ID")
        guardrail_version = os.getenv("GUARDRAIL_VERSION", "DRAFT")

        if not guardrail_id:
            _logger.warning("GUARDRAIL_ID が未設定です。ガードレールなしで動作します。")
            print("[WARNING] GUARDRAIL_ID が未設定です。ガードレールなしで動作します。", flush=True)

        return BedrockModel(
            model_id=cls.DEFAULT_MODEL_ID,
            guardrail_id=guardrail_id,
            guardrail_version=guardrail_version,
            guardrail_trace="enabled",
        )
