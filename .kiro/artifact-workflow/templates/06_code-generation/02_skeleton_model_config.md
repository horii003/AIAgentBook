# スケルトン: Bedrockモデル設定 (config/model_config.py)

## 概要

各エージェントが使用するBedrockモデルの設定を一元管理する。
モデルIDやガードレール設定をプロジェクト要件に応じて変更する。

## ファイル配置

`config/model_config.py`

## スケルトンコード

```python
"""Bedrockモデル設定

このファイルでは、各エージェントが使用するBedrockモデルの設定を定義します。
モデルやパラメータを変更する場合は、このファイルを編集してください。
"""
from strands.models import BedrockModel


class ModelConfig:
    """Bedrockモデル設定クラス"""

    # モデルID（プロジェクト要件に応じて変更）
    # 日本リージョンの場合: "jp.anthropic.claude-sonnet-4-5-20250929-v1:0"
    DEFAULT_MODEL_ID = "{リージョン}.anthropic.{モデル名}"

    # ガードレール設定（Amazon Bedrockで作成したガードレールIDを設定）
    # ガードレールが不要な場合はNoneを設定
    GUARDRAIL_ID = "{guardrail_id}"
    GUARDRAIL_VERSION = "DRAFT"

    @classmethod
    def get_model(cls) -> BedrockModel:
        """
        BedrockModelインスタンスを取得

        Returns:
            BedrockModel: 設定済みのBedrockModelインスタンス
        """
        return BedrockModel(
            model_id=cls.DEFAULT_MODEL_ID,
            guardrail_id=cls.GUARDRAIL_ID,
            guardrail_version=cls.GUARDRAIL_VERSION,
            guardrail_trace="enabled",
        )
```

## カスタマイズガイド

1. **モデルID**: リージョンとモデルファミリーに応じて `DEFAULT_MODEL_ID` を設定する
2. **ガードレール**: Amazon Bedrockで作成したガードレールのIDとバージョンを設定する。不要な場合は `GUARDRAIL_ID = None` とし、`get_model()` 内でガードレール設定を省略する
3. **モデルパラメータ**: 必要に応じて温度（temperature）や最大トークン数等のパラメータを追加する
