# スケルトン: エージェント共通ユーティリティ (agents/base_agent.py)

## 概要

全専門エージェントで共有するヘルパー関数・定数を定義する。
Session/HumanApprovalHook/LoopControlHook の生成と Agent インスタンスの組み立てを共通化し、
各専門エージェントファイルの重複を排除する。

専門エージェントは `create_specialist_agent` と `invoke_specialist_agent` を利用して
ビルド関数とツール関数を実装する（R9.11参照）。

## ファイル配置

`agents/base_agent.py`

## スケルトンコード

```python
"""エージェント共通ユーティリティ

全専門エージェントで共有するヘルパー関数・定数を定義する。
"""
import logging
from datetime import datetime
from typing import Callable
from dateutil.relativedelta import relativedelta
from strands import Agent, ToolContext, ModelRetryStrategy
from strands.agent.conversation_manager import SlidingWindowConversationManager
from handlers.human_approval_hook import HumanApprovalHook
from handlers.error_handler import LoopLimitError, ErrorHandler
from handlers.loop_control_hook import LoopControlHook
from session.session_manager import SessionManagerFactory
from config.model_config import ModelConfig

_logger = logging.getLogger(__name__)


def calculate_deadline(application_date: str, deadline_months: int) -> str:
    """
    申請日から申請期限を計算して返す。

    Args:
        application_date: 申請日（YYYY-MM-DD形式）
        deadline_months: 申請期限（経費発生日からの月数）。
                         settings.{agent}.deadline_months から渡す。

    Returns:
        str: 申請期限（YYYY-MM-DD形式）。パース失敗時は "要確認"。
    """
    # TODO: 詳細設計書に従い実装
    # - application_dateを datetime.strptime で "%Y-%m-%d" としてパース
    # - relativedelta(months=deadline_months) を加算
    # - strftime("%Y-%m-%d") で文字列に変換して返却
    # - 例外発生時は "要確認" を返却
    pass


def create_specialist_agent(
    session_id: str,
    system_prompt: str,
    tools: list,
    agent_name: str,
    window_size: int,
    max_iterations: int,
    max_attempts: int,
    initial_delay: int,
    max_delay: int,
) -> Agent:
    """
    専門エージェントの共通ファクトリー関数。

    Session/HumanApprovalHook/LoopControlHook の生成と Agent インスタンスの
    組み立てを共通化する。各専門エージェントのビルド関数はこれを呼び出す。

    Args:
        session_id: セッションID
        system_prompt: エージェント固有のシステムプロンプト
        tools: エージェント固有のツールリスト
        agent_name: LoopControlHook 用のエージェント名（ログ表示用）
        window_size: SlidingWindowConversationManager のウィンドウサイズ
        max_iterations: LoopControlHook の最大ループ回数
        max_attempts: ModelRetryStrategy のリトライ回数
        initial_delay: ModelRetryStrategy の初期遅延（秒）
        max_delay: ModelRetryStrategy の最大遅延（秒）

    Returns:
        Agent: 設定済みの Agent インスタンス
    """
    # TODO: 詳細設計書に従い実装
    # - SessionManagerFactory.create_session_manager(session_id) でセッション管理を作成
    # - HumanApprovalHook() を作成（R9.10参照）
    # - LoopControlHook(max_iterations=max_iterations, agent_name=agent_name) を作成
    # - Agent() を生成して返却（R9.5参照）
    #   return Agent(
    #       model=ModelConfig.get_model(),
    #       system_prompt=system_prompt,
    #       callback_handler=None,
    #       tools=tools,
    #       conversation_manager=SlidingWindowConversationManager(
    #           window_size=window_size,
    #           should_truncate_results=True,
    #           per_turn=False,
    #       ),
    #       retry_strategy=ModelRetryStrategy(
    #           max_attempts=max_attempts,
    #           initial_delay=initial_delay,
    #           max_delay=max_delay,
    #       ),
    #       hooks=[approval_hook, loop_hook],
    #       session_manager=session_manager,
    #   )
    pass


def invoke_specialist_agent(
    query: str,
    tool_context: ToolContext,
    agent_id: str,
    deadline_months: int,
    build_agent: Callable[[str, str, str, str], Agent],
) -> str:
    """
    専門エージェントの共通呼び出しラッパー。

    invocation_state の取得・deadline 計算・Agent 呼び出し・例外処理を共通化する。
    各専門エージェントのツール関数はこれを呼び出す。

    Args:
        query: ユーザーからの入力
        tool_context: Strands SDK が注入する ToolContext
        agent_id: ログ用エージェントID（例: "AG-002"）
        deadline_months: 申請期限の月数（settings.*.deadline_months）
        build_agent: (session_id, applicant_name, application_date, deadline) -> Agent を返すコールバック

    Returns:
        str: エージェントからの応答
    """
    # TODO: 詳細設計書に従い実装
    # - tool_context.invocation_state から applicant_name, application_date, session_id を取得
    # - _logger.info でログ出力
    # - calculate_deadline() で申請期限を計算
    # - build_agent(session_id, applicant_name, application_date, deadline) でエージェントを生成
    # - child_invocation_state を構築（applicant_name, application_date, session_id）
    # - agent(query, invocation_state=child_invocation_state) で呼び出し
    # - エラーハンドリング（R9.1参照）:
    #   - LoopLimitError: _logger.warning + ErrorHandler.handle_loop_limit_error(e) を返却
    #   - Exception: _logger.error(exc_info=True) + ErrorHandler.handle_unexpected_error(e) を返却
    pass
```

## カスタマイズガイド

1. **calculate_deadline**: `settings.{agent}.deadline_months` を受け取り、`dateutil.relativedelta` で月単位の期限を計算する
2. **create_specialist_agent**: 全専門エージェント共通のファクトリー。Session/Hook の作成と Agent の組み立てを集約する。HumanApprovalHook を自動的に組み込む
3. **invoke_specialist_agent**: `build_agent` コールバックのシグネチャは `(session_id, applicant_name, application_date, deadline) -> Agent` で固定。専門エージェントのビルド関数と対応する
4. **エラーハンドリング**: `LoopLimitError` は `_logger.warning` で記録し、`Exception` は `_logger.error(exc_info=True)` で記録する。両方とも `ErrorHandler` の static メソッドに委譲して文字列を返す
