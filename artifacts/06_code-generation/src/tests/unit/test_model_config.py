"""モデル設定の単体テスト"""

from unittest.mock import patch

from config.model_config import ModelConfig


class TestModelConfig:
    """ModelConfig のテスト"""

    def test_get_model_returns_instance(self):
        """get_model() がインスタンスを返すこと"""
        ModelConfig.get_model.cache_clear()
        model = ModelConfig.get_model()
        assert model is not None

    def test_get_model_cached(self):
        """lru_cache により同一インスタンスが返されること"""
        ModelConfig.get_model.cache_clear()
        model1 = ModelConfig.get_model()
        model2 = ModelConfig.get_model()
        assert model1 is model2

    def test_default_model_id(self):
        """デフォルトモデルIDが設定されていること"""
        assert "claude" in ModelConfig.DEFAULT_MODEL_ID.lower() or "anthropic" in ModelConfig.DEFAULT_MODEL_ID.lower()
