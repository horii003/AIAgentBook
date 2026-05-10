"""エージェント動作パラメータの一元管理

環境変数でエージェント別に上書き可能。
使い方:
    from config.settings import settings
    loop_hook = LoopControlHook(max_iterations=settings.orchestrator.max_iterations)
"""
from pydantic import Field
from pydantic_settings import BaseSettings


class _AgentSettings(BaseSettings):
    """全エージェント共通パラメータ"""
    max_iterations: int = Field(10, description="ReActループ最大回数")
    max_attempts: int = Field(6, description="モデル呼び出しリトライ回数")
    initial_delay: int = Field(4, description="リトライ初期遅延（秒）")
    max_delay: int = Field(240, description="リトライ最大遅延（秒）")


class OrchestratorSettings(_AgentSettings):
    """申請受付窓口エージェント（AG-001）固有パラメータ

    環境変数プレフィックス: ECAAS_ORCHESTRATOR_
    """
    window_size: int = Field(30, description="会話ウィンドウサイズ")
    max_turn_count: int = Field(30, description="対話回数上限")
    max_input_length: int = Field(500, description="入力文字数上限")

    model_config = {"env_prefix": "ECAAS_ORCHESTRATOR_", "extra": "ignore"}


class TransportAgentSettings(_AgentSettings):
    """交通費精算申請エージェント（AG-002）固有パラメータ

    環境変数プレフィックス: ECAAS_TRANSPORT_
    """
    window_size: int = Field(20, description="会話ウィンドウサイズ")
    deadline_months: int = Field(3, description="申請期限（月数）")
    approval_threshold: int = Field(10000, description="上長承認が必要な交通費合計の閾値（円）")

    model_config = {"env_prefix": "ECAAS_TRANSPORT_", "extra": "ignore"}


class ExpenseAgentSettings(_AgentSettings):
    """経費精算申請エージェント（AG-003）固有パラメータ

    環境変数プレフィックス: ECAAS_EXPENSE_
    """
    window_size: int = Field(20, description="会話ウィンドウサイズ")
    deadline_months: int = Field(3, description="申請期限（月数）")
    approval_threshold: int = Field(5000, description="上長承認が必要な経費合計の閾値（円）")

    model_config = {"env_prefix": "ECAAS_EXPENSE_", "extra": "ignore"}


class _Settings:
    """全設定の集約クラス。`settings.{agent_name}.max_iterations` のように参照する"""
    orchestrator: OrchestratorSettings = OrchestratorSettings()
    transport_agent: TransportAgentSettings = TransportAgentSettings()
    expense_agent: ExpenseAgentSettings = ExpenseAgentSettings()


settings = _Settings()
