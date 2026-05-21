---
version: "2.0.0"
last_updated: "2026-05-21"
updated_by: ""
---

# スケルトン: 評価テスト

## 概要

LLM-as-Judge 方式でエージェントの品質を自動評価するスクリプト群のテンプレート。
`evals/helpers.py`（評価共通ヘルパー）と `evals/eval_{evaluation_name}.py`（評価スクリプト）で構成する。

Strands Agents Evals フレームワーク前提。評価対象エージェントの種類（申請処理・検索・対話等）
を問わず適用できる構造とする。

> **規約**: `.kiro/steering/00_rule_project_conventions.md`（RE1〜RE6）に従うこと

---

## Part 1: helpers.py

### ファイル配置

`evals/helpers.py`

### スケルトンコード

```python
"""評価用共通ヘルパー

既存のエージェントコードを修正せず、評価に必要なユーティリティを提供する。
- ブロッキングフックの自動承認パッチ
- 評価用エージェントファクトリ（テレメトリ trace_attributes 付き）
- ActorSimulator を使った動的マルチターン会話
- StrandsEvalsTelemetry によるスパン自動キャプチャ
"""

import logging

from strands import Agent
from strands.agent.conversation_manager import SlidingWindowConversationManager
from strands_evals import ActorSimulator
from strands_evals.telemetry import StrandsEvalsTelemetry

logger = logging.getLogger(__name__)


# ============================================================
# テレメトリ初期化（モジュールレベルシングルトン）
# ============================================================

telemetry = StrandsEvalsTelemetry().setup_in_memory_exporter()
memory_exporter = telemetry.in_memory_exporter


# ============================================================
# ブロッキングフック パッチ
# ============================================================

def patch_human_approval_hook():
    """ブロッキングフックを自動承認に差し替える。

    既存コードのフックは input() でコンソール入力を求めるため、
    評価時にブロックされる。approval_callback を自動承認に置き換えることで
    ツールの実行をノンブロッキングにする。

    注意: この関数はモジュールレベルでクラスを書き換えるため、
    他のエージェントモジュールをインポートする **前** に呼び出すこと。
    """
    # TODO: 実装コードのフッククラスを読み、__init__ を差し替える
    # パターン:
    #   from handlers.{hook_module} import {HookClass}
    #   _original_init = {HookClass}.__init__
    #   def _patched_init(self, approval_callback=None):
    #       _original_init(self, approval_callback=lambda *a: (True, ""))
    #   {HookClass}.__init__ = _patched_init
    pass


# ============================================================
# モデル・状態ファクトリ
# ============================================================

def get_model():
    """評価器用のモデルを取得する。"""
    # TODO: 実装コードの ModelConfig を参照して返す
    pass


def create_invocation_state(session_id: str):
    """評価用の InvocationState を作成する。

    Args:
        session_id: テストケース固有のセッションID
    """
    # TODO: 実装コードの InvocationState モデルに合わせて生成する
    # - 評価用のデフォルト値（申請者名・申請日等）を設定する
    pass


# ============================================================
# エージェントファクトリ
# ============================================================

def {agent_factory}(session_id: str):
    """評価用のエージェントを作成する。

    既存のエージェントクラスが input() ループを持つ場合は直接使えない。
    同じ構成（モデル・プロンプト・ツール・フック）で Agent を直接生成する。

    Args:
        session_id: セッションID（テレメトリの trace_attributes に設定）
    """
    # TODO: 実装コードのエージェント構成を読み、同一構成で Agent を直接生成する
    # パターン:
    #   from agents.{specialist}_agent import {specialist}_agent
    #   from config.model_config import ModelConfig
    #   from prompt.prompt_{agent} import {AGENT}_SYSTEM_PROMPT
    #   from handlers.loop_control_hook import LoopControlHook
    #
    #   return Agent(
    #       model=ModelConfig.get_model(),
    #       system_prompt={AGENT}_SYSTEM_PROMPT,
    #       tools=[{specialist_a}_agent, {specialist_b}_agent],
    #       conversation_manager=SlidingWindowConversationManager(
    #           window_size=...,
    #           should_truncate_results=True,
    #           per_turn=False,
    #       ),
    #       callback_handler=None,
    #       hooks=[LoopControlHook(max_iterations=..., agent_name="...")],
    #       trace_attributes={
    #           "session.id": session_id,
    #           "gen_ai.conversation.id": session_id,
    #       },
    #   )
    pass


# ============================================================
# 会話実行（ActorSimulator ベース）
# ============================================================

def run_actor_conversation(
    agent, case, invocation_state_dict: dict, max_turns: int = {max_turns}
) -> list[dict]:
    """ActorSimulator を使ってエージェントと動的マルチターン会話を実行する。

    ActorSimulator が LLM ベースのユーザーシミュレータとして動的に応答を生成し、
    エージェントの応答に基づいて次のユーザー発話を決定する。

    Args:
        agent: strands Agent インスタンス
        case: strands_evals Case オブジェクト
        invocation_state_dict: InvocationState を model_dump() した dict
        max_turns: 最大ターン数

    Returns:
        list[dict]: 各ターンの {"user_prompt", "agent_response"} リスト
    """
    # TODO: 設計書のユーザーシミュレーター設計に従い実装
    # パターン:
    #   user_sim = ActorSimulator.from_case_for_user_simulator(
    #       case=case, model=get_model(), max_turns=max_turns,
    #   )
    #   turns = []
    #   user_message = case.input
    #   while user_sim.has_next():
    #       # memory_exporter.clear() は呼ばない — 全ターンのスパンを蓄積する
    #       result = agent(user_message, invocation_state=invocation_state_dict)
    #       response = str(result)
    #       turns.append({"user_prompt": user_message, "agent_response": response})
    #       user_result = user_sim.act(response)
    #       user_message = str(user_result.structured_output.message)
    #   return turns
    pass
```

### カスタマイズガイド

1. **テレメトリ**: `StrandsEvalsTelemetry().setup_in_memory_exporter()` はモジュールレベルで1回だけ実行する。`run_eval_task` の先頭で `memory_exporter.clear()` して各ケースのスパンを分離する
2. **フックパッチ**: `__init__` のモンキーパッチが基本パターン。他のエージェントモジュールをインポートする前に呼ぶこと
3. **エージェントファクトリ**: 既存のエージェントクラスが対話ループ（input()）を持つ場合、ループ部分を除いて Agent を直接生成する。`trace_attributes` にセッションIDを渡すことでテレメトリを分離する
4. **マルチターン会話**: `ActorSimulator.from_case_for_user_simulator()` で生成し、`has_next()` / `act()` でループする。ループ内で `memory_exporter.clear()` を呼ばないこと（全ターンのスパンを蓄積して Session を構築するため）
5. **シングルターン評価のみの場合**: `run_actor_conversation` は不要

---

## Part 2: eval_{evaluation_name}.py（マルチターン版）

### ファイル配置

`evals/eval_{evaluation_name}.py`

### スケルトンコード

```python
"""{evaluation_description}

評価レベル: SESSION_LEVEL
実行方法: python evals/eval_{evaluation_name}.py
"""

import sys
import os
import json
import logging
import warnings
from dotenv import load_dotenv

# ---- 初期設定 ----
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv()

from helpers import (
    patch_human_approval_hook, {agent_factory}, run_actor_conversation,
    memory_exporter, get_model, create_invocation_state,
)

patch_human_approval_hook()

from strands_evals import Case, Experiment
from strands_evals.evaluators import {EvaluatorClass}
from strands_evals.mappers import StrandsInMemorySessionMapper

_LOGS_DIR = os.path.join("evals", "logs")
_REPORTS_DIR = os.path.join(_LOGS_DIR, "reports")
os.makedirs(_REPORTS_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(
            os.path.join(_LOGS_DIR, "eval_{evaluation_name}.log"),
            encoding="utf-8",
        ),
    ],
)
logger = logging.getLogger(__name__)
warnings.filterwarnings("ignore")
logging.getLogger("strands").setLevel(logging.WARNING)
logging.getLogger("strands.event_loop.event_loop").setLevel(logging.CRITICAL)


# ================================================================
# テストケース定義
# ================================================================

EVAL_CASES = [
    Case(
        name="{case_name_1}",
        input="{user_input_1}",
        metadata={
            "task_description": "{task_description_1}",
            "{metadata_judge_key}": "{judge_criteria_1}",
        },
    ),
    # TODO: 詳細設計書のケース一覧に従い全ケースを追加
]


# ================================================================
# タスク関数
# ================================================================

def run_eval_task(case: Case) -> dict:
    """Experiment に渡す task 関数（マルチターン評価）。"""
    # TODO: 詳細設計書のマルチターン実行フローに従い実装
    # パターン:
    #   1. memory_exporter.clear()  ← 前ケースのスパン混入防止（ケース開始時に1回のみ）
    #   2. {agent_factory}(session_id) でエージェント生成
    #   3. create_invocation_state(session_id) で状態生成
    #   4. run_actor_conversation(agent, case, state.model_dump()) で会話実行
    #      ※ run_actor_conversation 内では clear しない（全ターンのスパンを蓄積）
    #   5. memory_exporter.get_finished_spans() → StrandsInMemorySessionMapper で Session 構築
    #   6. {"output": 最終応答, "trajectory": session} を返す
    pass


# ================================================================
# メイン
# ================================================================

def main():
    """評価実験を実行し、レポートを保存する。"""
    # TODO: 詳細設計書の実験実行設計に従い実装
    # パターン:
    #   1. {EvaluatorClass}(model=get_model()) で評価器生成
    #   2. Experiment(cases=EVAL_CASES, evaluators=[evaluator]) で実験構成
    #   3. experiment.run_evaluations(run_eval_task) で評価実行
    #   4. レポートを JSON 保存（ensure_ascii=False, indent=2）
    #   5. report.run_display() でコンソール表示
    pass


if __name__ == "__main__":
    main()
```

---

## Part 3: eval_{evaluation_name}.py（シングルターン版）

マルチターン版（Part 2）から以下を変更する。

### 差分1: import

`run_actor_conversation` を除去する。

```python
from helpers import (
    patch_human_approval_hook, {agent_factory},
    memory_exporter, get_model, create_invocation_state,
)
```

### 差分2: run_eval_task

```python
def run_eval_task(case: Case) -> dict:
    """Experiment に渡す task 関数（シングルターン評価）。"""
    # TODO: 詳細設計書のシングルターン実行フローに従い実装
    # パターン:
    #   1. memory_exporter.clear()  ← 前ケースのスパン混入防止（必須）
    #   2. {agent_factory}(session_id) でエージェント生成
    #   3. create_invocation_state(session_id) で状態生成
    #   4. agent(case.input, invocation_state=state.model_dump()) で1ターン送信
    #   5. memory_exporter.get_finished_spans() → StrandsInMemorySessionMapper で Session 構築
    #   6. {"output": response, "trajectory": session} を返す
    pass
```

### 差分3: EVAL_CASES の metadata キー

マルチターン版の `"{metadata_judge_key}"` を評価器に対応するキーに変更する。

```python
# マルチターン（GoalSuccessRateEvaluator）の場合
metadata={"task_description": "...", "goal": "..."}

# シングルターン（ToolSelectionAccuracyEvaluator）の場合
metadata={"task_description": "...", "expected_tool": "..."}
```

---

## カスタマイズガイド

1. **評価スクリプトの追加**: 新しい評価指標を追加する場合、Part 2 または Part 3 をコピーしてファイルを作成する
2. **評価器の差し替え**: `{EvaluatorClass}` を目的の評価器クラスに置き換え、`metadata` のキーも対応して変更する
3. **テストケースの追加**: `EVAL_CASES` に `Case(...)` を追記する。マルチターンの場合、`input` は会話の起点のみ記述する（2ターン目以降は ActorSimulator が自動生成）
4. **初期設定の順序**: sys.path → load_dotenv → helpers import → patch → 他のimport。patch はエージェントモジュールのインポート前に呼ぶこと
