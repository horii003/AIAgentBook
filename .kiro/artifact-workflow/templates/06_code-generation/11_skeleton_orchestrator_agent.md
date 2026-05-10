# スケルトン: オーケストレーターエージェント (agents/orchestrator_agent.py)

## 概要

ユーザーからの依頼を受け付け、適切な専門エージェントに振り分けるオーケストレーター。
アプリケーションのメインインタラクションループを管理する。

## ファイル配置

`agents/orchestrator_agent.py`

## スケルトンコード

```python
"""オーケストレーターエージェント

ユーザーからの依頼を受け付け、適切な専門エージェントに振り分ける。
{業務ドメインの説明}を担当する受付窓口として機能する。
"""

from datetime import datetime
from strands import Agent
from strands import ModelRetryStrategy
from strands.agent.conversation_manager import SlidingWindowConversationManager
from agents.specialist_a_agent import specialist_a_agent
from agents.specialist_b_agent import specialist_b_agent
from session.session_manager import SessionManagerFactory
from handlers.error_handler import ErrorHandler, LoopLimitError
from handlers.loop_control_hook import LoopControlHook
from prompt.prompt_orchestrator import ORCHESTRATOR_SYSTEM_PROMPT
from config.model_config import ModelConfig
from models.data_models import InvocationState


class OrchestratorAgent:
    """オーケストレーターエージェントクラス

    ユーザーとの対話を管理し、専門エージェントへの振り分けを行う。
    """

    def __init__(self):
        self._session_id = None
        self._session_manager = None
        self.agent = None
        self._error_handler = ErrorHandler()

    def _initialize(self):
        """初期化処理"""
        # TODO: 詳細設計書に従い実装
        # - 業務要件に応じた初期情報の収集
        #
        # - セッションマネージャーの作成
        #   self._session_manager = SessionManagerFactory.create_session_manager(self._session_id)
        #
        # - LoopControlHookの作成
        #   loop_control_hook = LoopControlHook(
        #       max_iterations=10,
        #       agent_name="{オーケストレーターの表示名}"
        #   )
        #
        # - Agentインスタンスの生成
        #   self.agent = Agent(
        #       model=ModelConfig.get_model(),
        #       system_prompt=ORCHESTRATOR_SYSTEM_PROMPT,
        #       tools=[specialist_a_agent, specialist_b_agent],
        #       conversation_manager=SlidingWindowConversationManager(
        #           window_size=30,
        #           should_truncate_results=True,
        #           per_turn=False
        #       ),
        #       callback_handler=None,
        #       retry_strategy=ModelRetryStrategy(
        #           max_attempts=6, initial_delay=4, max_delay=240
        #       ),
        #       hooks=[loop_control_hook],
        #       session_manager=self._session_manager
        #   )
        pass

    def run(self):
        """メインインタラクションループ"""
        # TODO: 詳細設計書に従い実装
        # - 初期化処理の呼び出し
        # - 対話ループの開始
        #   - ユーザー入力の受付
        #   - 終了条件の判定
        #   - invocation_stateの構築（InvocationState → model_dump()）
        #   - エージェント呼び出しと応答表示
        #   - エラーハンドリング（R9.1準拠）
        pass
```

## カスタマイズガイド

1. **ツール（専門エージェント）の追加**: `tools` リストに新しい専門エージェントのツール関数を追加する
2. **InvocationStateの構築**: `models/data_models.py` のInvocationStateに業務固有のフィールドを追加した場合、stateの構築を更新する
3. **対話ループの制御**: 業務要件に応じて終了条件やリセット処理を定義する
