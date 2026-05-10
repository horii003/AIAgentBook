# スケルトン: 専門エージェント (agents/specialist_{name}_agent.py)

## 概要

オーケストレーターからAgent as Toolsパターンで呼び出される専門エージェント。
ドメイン固有の処理（情報収集、検証、計算、出力生成等）を担当する。
各専門エージェントごとにファイルを作成する。

エージェント生成・呼び出しの共通処理は `agents/base_agent.py` の
`create_specialist_agent` / `invoke_specialist_agent` に集約する（R9.11参照）。

## ファイル配置

`agents/specialist_a_agent.py`（専門エージェントAの場合）
`agents/specialist_b_agent.py`（専門エージェントBの場合）

## スケルトンコード

```python
"""専門エージェントA

{専門エージェントAの担当するドメインの説明}を担当する専門エージェント。
オーケストレーターからAgent as Toolsパターンで呼び出される。
"""
from strands import Agent, tool, ToolContext
from tools.{domain}_tools import {tool_function_1}, {tool_function_2}
from tools.output_generator import {specialist_a_output_generator}
from prompt.prompt_specialist_a import get_specialist_a_system_prompt
from knowledge.{domain}_policies import get_{domain}_rules
from config.settings import settings
from agents.base_agent import create_specialist_agent, invoke_specialist_agent


# ============ エージェントの初期化 ============

def _build_specialist_a_agent(
    session_id: str,
    applicant_name: str,
    application_date: str,
    deadline: str,
) -> Agent:
    """
    専門エージェントAのインスタンスを作成するビルド関数。

    Args:
        session_id: セッションID
        applicant_name: 申請者名
        application_date: 申請日（YYYY-MM-DD形式）
        deadline: 申請期限（YYYY-MM-DD形式）

    Returns:
        Agent: 専門エージェントAのインスタンス
    """
    # TODO: 詳細設計書に従い実装
    # - settingsから該当エージェントの設定を取得
    #   cfg = settings.{specialist_a}
    # - システムプロンプトの生成
    #   system_prompt = get_specialist_a_system_prompt(
    #       applicant_name=applicant_name,
    #       application_date=application_date,
    #       deadline=deadline,
    #       {domain}_rules=get_{domain}_rules(),
    #   )
    # - create_specialist_agent()でエージェントを生成して返却（R9.11.1参照）
    #   return create_specialist_agent(
    #       session_id=session_id,
    #       system_prompt=system_prompt,
    #       tools=[{tool_function_1}, {tool_function_2}, {specialist_a_output_generator}],
    #       agent_name="{専門エージェントAの表示名}",
    #       window_size=cfg.window_size,
    #       max_iterations=cfg.max_iterations,
    #       max_attempts=cfg.max_attempts,
    #       initial_delay=cfg.initial_delay,
    #       max_delay=cfg.max_delay,
    #   )
    pass


# ============ Agent as Tools ============

@tool(context=True)
def specialist_a_agent(query: str, tool_context: ToolContext) -> str:
    """
    専門エージェントAツール

    {専門エージェントAの処理の説明}を実行します。
    会話履歴を保持して、複数回の呼び出しでも段階的に情報を収集します。

    Args:
        query: ユーザーからの入力や質問

    Note:
        tool_context は Strands SDK が @tool(context=True) により自動注入する。
        LLM へのツールスキーマには含まれず、LLM が値を指定することもない。

        呼び出しのたびに Agent インスタンスを新規生成するが、FileSessionManager により
        会話履歴はファイルに永続化される。同一 session_id を渡すことで、
        次回呼び出し時にファイルから前回の会話履歴が復元され、段階的な情報収集が継続される。

    Returns:
        str: エージェントからの応答
    """
    # TODO: 詳細設計書に従い実装
    # - invoke_specialist_agent()で呼び出す（R9.11.2参照）
    #   return invoke_specialist_agent(
    #       query=query,
    #       tool_context=tool_context,
    #       agent_id="AG-00X",
    #       deadline_months=settings.{specialist_a}.deadline_months,
    #       build_agent=_build_specialist_a_agent,
    #   )
    pass
```


## 専門エージェント追加手順

新しい専門エージェントを追加する場合、以下のファイルを作成・更新する：

1. **`agents/specialist_{name}_agent.py`**: このテンプレートをコピーして新規作成
2. **`prompt/prompt_specialist_{name}.py`**: 新エージェントのシステムプロンプトを定義
3. **`knowledge/{domain}_policies.py`**: 新ドメインのビジネスルールを定義（必要な場合）
4. **`tools/{domain}_tools.py`**: 新ドメインのツール関数を定義（必要な場合）
5. **`models/data_models.py`**: 新ドメインのデータモデルを追加（必要な場合）
6. **`agents/orchestrator_agent.py`**: `tools` リストに新エージェントのツール関数を追加
7. **`prompt/prompt_orchestrator.py`**: 振り分け基準テーブルに新エージェントを追加

## カスタマイズガイド

1. **ビルド関数のシグネチャ**: `_build_{name}_agent(session_id, applicant_name, application_date, deadline)` の固定シグネチャにする。`invoke_specialist_agent` が `build_agent` コールバックとして呼び出すため
2. **settings の参照**: エージェントごとのパラメータは `config/settings.py` の `settings.{agent_name}` から取得する（R9.11参照）
3. **HumanApprovalHookの適用**: `create_specialist_agent` は自動的に `HumanApprovalHook` と `LoopControlHook` を組み込む。承認対象ツール名は `HumanApprovalHook.APPROVAL_REQUIRED_TOOLS` に設定する
4. **invocation_stateの伝播**: `invoke_specialist_agent` が `applicant_name`, `application_date`, `session_id` を自動的に取得・伝播する
