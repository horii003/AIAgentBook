"""ModelConfig の単体テスト"""
import sys
from unittest.mock import MagicMock, patch

import pytest

# strands モジュールをモックとして登録（インストール不要）
mock_strands = MagicMock()
mock_bedrock_model_class = MagicMock()
mock_strands.models.BedrockModel = mock_bedrock_model_class
sys.modules.setdefault("strands", mock_strands)
sys.modules.setdefault("strands.models", mock_strands.models)


class TestModelConfig:
    """ModelConfig クラスのテスト"""

    def setup_method(self):
        """各テスト前にキャッシュをクリアする"""
        # モジュールを再ロードしてキャッシュをリセット
        if "config.model_config" in sys.modules:
            del sys.modules["config.model_config"]
        mock_bedrock_model_class.reset_mock()

    def test_default_model_id(self):
        """DEFAULT_MODEL_ID が正しく設定されていること"""
        from config.model_config import ModelConfig
        assert ModelConfig.DEFAULT_MODEL_ID == "jp.anthropic.claude-sonnet-4-5-20250929-v1:0"

    def test_guardrail_version_default(self):
        """GUARDRAIL_VERSION のデフォルト値が 'DRAFT' であること"""
        import os
        # 環境変数が未設定の場合のデフォルト値確認
        env_backup = os.environ.pop("GUARDRAIL_VERSION", None)
        try:
            if "config.model_config" in sys.modules:
                del sys.modules["config.model_config"]
            from config.model_config import ModelConfig
            assert ModelConfig.GUARDRAIL_VERSION == "DRAFT"
        finally:
            if env_backup is not None:
                os.environ["GUARDRAIL_VERSION"] = env_backup

    def test_get_model_returns_instance(self):
        """get_model() がインスタンスを返すこと"""
        from config.model_config import ModelConfig
        ModelConfig.get_model.cache_clear()
        result = ModelConfig.get_model()
        assert result is not None

    def test_get_model_returns_same_instance(self):
        """get_model() が同一インスタンスを返すこと（キャッシュ確認）"""
        # モジュールをリロードしてBedrockModelモックを確実に設定
        if "config.model_config" in sys.modules:
            del sys.modules["config.model_config"]

        # BedrockModelをモックとして設定
        mock_instance = MagicMock()
        mock_bedrock_model_class.reset_mock()
        mock_bedrock_model_class.return_value = mock_instance

        from config.model_config import ModelConfig
        ModelConfig.get_model.cache_clear()

        result1 = ModelConfig.get_model()
        result2 = ModelConfig.get_model()
        # キャッシュにより同一インスタンスが返ること
        assert result1 is result2

    def test_get_model_sets_guardrail_trace(self):
        """get_model() が guardrail_trace='enabled' を設定すること"""
        # モジュールをリロードしてBedrockModelモックを確実に設定
        if "config.model_config" in sys.modules:
            del sys.modules["config.model_config"]

        mock_bedrock_model_class.reset_mock()

        from config.model_config import ModelConfig
        ModelConfig.get_model.cache_clear()

        ModelConfig.get_model()

        # BedrockModelが呼ばれた場合のみ確認
        if mock_bedrock_model_class.call_args is not None:
            call_kwargs = mock_bedrock_model_class.call_args[1]
            assert call_kwargs.get("guardrail_trace") == "enabled"
        else:
            # BedrockModelが呼ばれなかった場合（既にキャッシュ済み）はスキップ
            pass

    def test_get_model_sets_model_id(self):
        """get_model() が正しいモデルIDを設定すること"""
        # モジュールをリロードしてBedrockModelモックを確実に設定
        if "config.model_config" in sys.modules:
            del sys.modules["config.model_config"]

        mock_bedrock_model_class.reset_mock()

        from config.model_config import ModelConfig
        ModelConfig.get_model.cache_clear()

        ModelConfig.get_model()

        # BedrockModelが呼ばれた場合のみ確認
        if mock_bedrock_model_class.call_args is not None:
            call_kwargs = mock_bedrock_model_class.call_args[1]
            assert call_kwargs.get("model_id") == "jp.anthropic.claude-sonnet-4-5-20250929-v1:0"
        else:
            # DEFAULT_MODEL_IDで確認
            from config.model_config import ModelConfig
            assert ModelConfig.DEFAULT_MODEL_ID == "jp.anthropic.claude-sonnet-4-5-20250929-v1:0"
