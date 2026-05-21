"""Bedrockモデル設定の単体テスト"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from unittest.mock import patch, MagicMock
from strands.models import BedrockModel


class TestModelConfig:
    """ModelConfig クラスのテスト"""

    def test_default_model_id(self):
        """DEFAULT_MODEL_ID が期待値と一致すること"""
        from config.model_config import ModelConfig
        assert ModelConfig.DEFAULT_MODEL_ID == "jp.anthropic.claude-sonnet-4-5-20250929-v1:0"

    def test_get_model_returns_bedrock_model(self):
        """get_model() が BedrockModel インスタンスを返すこと"""
        from config.model_config import ModelConfig
        # キャッシュをクリアして新しいインスタンスを取得
        ModelConfig.get_model.cache_clear()
        model = ModelConfig.get_model()
        assert isinstance(model, BedrockModel)

    def test_get_model_returns_same_instance(self):
        """get_model() を複数回呼び出しても同一インスタンスが返ること（キャッシュ確認）"""
        from config.model_config import ModelConfig
        ModelConfig.get_model.cache_clear()
        model1 = ModelConfig.get_model()
        model2 = ModelConfig.get_model()
        assert model1 is model2
