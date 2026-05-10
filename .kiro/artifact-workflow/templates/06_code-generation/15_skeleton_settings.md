# スケルトン: エージェント動作パラメータ設定 (config/settings.py)

## 概要

全エージェントの動作パラメータを一元管理するモジュール。
`pydantic-settings` の `BaseSettings` を使い、環境変数でエージェント別に上書き可能。
各エージェントのパラメータは `settings.{エージェント名}.{パラメータ名}` で参照する。

このモジュールは `agents/base_agent.py` や各専門エージェントが参照する。

## ファイル配置

`config/settings.py`

## スケルトンコード

```python
"""エージェント動作パラメータの一元管理

環境変数でエージェント別に上書き可能（プレフィックスはクラスごとに異なる）。
例: {ECAAS_AGENT_A}_MAX_ITERATIONS=15 を .env に追加するだけでチューニングできる。

使い方:
    from config.settings import settings
    loop_hook = LoopControlHook(max_iterations=settings.{agent_a}.max_iterations)
"""
from pydantic import Field
from pydantic_settings import BaseSettings


class _AgentSettings(BaseSettings):
    """全エージェント共通パラメータ"""
    max_iterations: int = Field(10, description="ReActループ最大回数")
    max_attempts: int = Field(6, description="モデル呼び出しリトライ回数")
    initial_delay: int = Field(4, description="リトライ初期遅延（秒）")
    max_delay: int = Field(240, description="リトライ最大遅延（秒）")


# TODO: 詳細設計書に従い各エージェントの設定クラスを実装
# オーケストレーター設定の例:
# class OrchestratorSettings(_AgentSettings):
#     """{AG-001名称}（オーケストレーター）固有パラメータ
#
#     環境変数プレフィックス: {ECAAS_ORCHESTRATOR_}
#     例: {ECAAS_ORCHESTRATOR_}_MAX_ITERATIONS=15
#     """
#     window_size: int = Field(30, description="会話ウィンドウサイズ（ターン数）")
#     max_turn_count: int = Field(30, description="対話回数上限")
#     max_input_length: int = Field(500, description="入力文字数上限")
#
#     model_config = {"env_prefix": "{ECAAS_ORCHESTRATOR_}", "extra": "ignore"}

# 専門エージェント設定の例:
# class SpecialistASettings(_AgentSettings):
#     """{AG-00X名称}（専門エージェントA）固有パラメータ
#
#     環境変数プレフィックス: {ECAAS_SPECIALIST_A_}
#     例: {ECAAS_SPECIALIST_A_}_MAX_ITERATIONS=15
#     """
#     window_size: int = Field(20, description="会話ウィンドウサイズ（ターン数）")
#     deadline_months: int = Field(3, description="申請期限（経費発生日からの月数）")
#
#     model_config = {"env_prefix": "{ECAAS_SPECIALIST_A_}", "extra": "ignore"}


class _Settings:
    """全設定の集約クラス。`settings.{agent_name}.max_iterations` のように参照する"""
    # TODO: エージェントごとの設定インスタンスを追加
    # orchestrator: OrchestratorSettings = OrchestratorSettings()
    # specialist_a: SpecialistASettings = SpecialistASettings()
    pass


settings = _Settings()
```

## カスタマイズガイド

1. **エージェントクラス**: 各専門エージェントごとに `_AgentSettings` を継承したクラスを定義する。エージェントID・表示名に対応するクラス名にする
2. **環境変数プレフィックス**: `model_config = {"env_prefix": "{PREFIX}_", "extra": "ignore"}` でエージェントごとに異なるプレフィックスを設定する
3. **window_size**: オーケストレーターは30、専門エージェントは15〜20を目安とする（R9.5.3参照）
4. **deadline_months**: 申請期限は業務要件に応じて設定する。`agents/base_agent.py` の `calculate_deadline` が参照する
5. **_Settings集約クラス**: 全エージェントの設定インスタンスをフィールドとして持つ。`settings` モジュールレベル変数として参照する
