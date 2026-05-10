"""ModelConfigの単体テスト"""
import pytest
from unittest.mock import patch, MagicMock


class TestModelConfig:
    def test_get_model_returns_bedrock_model(self):
        """get_model()がBedrockModelインスタンスを返すこと"""
        with patch("strands.models.BedrockModel") as mock_bedrock:
            mock_instance = MagicMock()
            mock_bedrock.return_value = mock_instance
            # lru_cacheをクリアしてから実行
            from config.model_config import ModelConfig
            ModelConfig.get_model.cache_clear()
            result = ModelConfig.get_model()
            assert result is not None

    def test_default_model_id(self):
        """DEFAULT_MODEL_IDが設定されていること"""
        from config.model_config import ModelConfig
        assert ModelConfig.DEFAULT_MODEL_ID == "jp.anthropic.claude-sonnet-4-5-20250929-v1:0"
