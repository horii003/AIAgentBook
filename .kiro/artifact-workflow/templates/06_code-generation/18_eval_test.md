---
version: "1.0.0"
last_updated: "2026-05-02"
updated_by: ""
---

# スケルトン: 評価テスト (`evals/eval_{evaluation_name}.py`)

## 概要

LLM-as-Judge 方式でエージェントの品質を自動評価するスクリプトのテンプレートです。エージェントの実行軌跡（trajectory）を参照し、二値スコア（Yes=1.0 / No=0.0）で判定します。マルチターン評価（ゴール達成率）とシングルターン評価（ツール選択精度）の2タイプを提供します。

> **参照元（評価設計資料）:**
> - `artifacts/05_detailed-design/outputs/評価テスト詳細設計.md` - 評価詳細設計

## ファイル配置

`evals/eval_{evaluation_name}.py`

---

## 評価タイプの選択

| 項目 | マルチターン評価 | シングルターン評価 |
|------|----------------|-----------------|
| **評価器クラス** | `GoalSuccessRateEvaluator` | `ToolSelectionAccuracyEvaluator` |
| **評価レベル** | SESSION_LEVEL | TURN_LEVEL |
| **実行方式** | ActorSimulator による動的会話 | 1ターンのみ送信 |
| **metadata キー** | `"goal"` | `"expected_tool"` |
| **用途** | エンドツーエンドのゴール達成検証 | ルーティング精度検証 |

---

## スケルトンコード（マルチターン評価 — GoalSuccessRateEvaluator）

```python
"""{evaluation_description}

評価レベル: SESSION_LEVEL
  - StrandsEvalsTelemetry でエージェントの実行スパンを自動キャプチャ
  - StrandsInMemorySessionMapper でスパンから Session を自動構築
  - {EvaluatorClass} が全ターン・全ツール呼び出しを LLM-as-Judge で判定

実行方法:
    python evals/eval_{evaluation_name}.py
"""

import sys
import os
import json
import logging
import warnings
from dotenv import load_dotenv
from helpers import (
    patch_human_approval_hook, {agent_factory}, run_actor_conversation,
    memory_exporter, get_model, create_invocation_state,
)
from strands_evals import Case, Experiment
from strands_evals.evaluators import {EvaluatorClass}
from strands_evals.mappers import StrandsInMemorySessionMapper

# ---- 初期設定（必須・順序固定） ----
# [1] 標準入出力 UTF-8 設定
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")
# [2] sys.path へプロジェクトルート追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# [3] load_dotenv
load_dotenv()
# [4] patch_human_approval_hook（load_dotenv の直後に必須）
patch_human_approval_hook()

# ---- ログ設定 ----
# [5] ログ設定
_LOGS_DIR = os.path.join("evals", "logs")
os.makedirs(_LOGS_DIR, exist_ok=True)
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
# [6] warnings 抑制
warnings.filterwarnings("ignore")
# [7] strands SDK ログ抑制（評価時は不要なため）
logging.getLogger("strands").setLevel(logging.WARNING)
logging.getLogger("strands.event_loop.event_loop").setLevel(logging.CRITICAL)


# ================================================================
# テストケース定義（Case オブジェクト）
# ================================================================

EVAL_CASES = [
    Case(
        name="{case_name_1}",
        input="{user_input_1}",
        metadata={
            "task_description": "{task_description_1}",
            "goal": "{judge_criteria_1}",
        },
    ),
    # TODO: 詳細設計書のテストケース一覧に従いケースを追加する
]


# ================================================================
# タスク関数（Experiment に渡す）
# ================================================================

def run_eval_task(case: Case) -> dict:
    """Experiment に渡す task 関数（マルチターン評価）。

    Args:
        case: strands_evals Case オブジェクト

    Returns:
        dict: {"output": 最終応答, "trajectory": Session オブジェクト}
    """
    session_id = case.session_id
    logger.info("=== ケース '%s' 開始 (session: %s) ===", case.name, session_id)

    # 前のケースのスパンが混入しないようにリセット（必須）
    memory_exporter.clear()

    # ---- エージェント作成 ----
    agent = {agent_factory}(session_id)

    # ---- InvocationState ----
    state = create_invocation_state(session_id)

    # ---- ActorSimulator による動的会話実行 ----
    turns = run_actor_conversation(agent, case, state.model_dump())

    # ---- テレメトリスパンから Session を自動構築 ----
    finished_spans = memory_exporter.get_finished_spans()
    mapper = StrandsInMemorySessionMapper()
    session = mapper.map_to_session(finished_spans, session_id=session_id)

    final_response = turns[-1]["agent_response"] if turns else ""

    return {"output": final_response, "trajectory": session}


# ================================================================
# メイン
# ================================================================

def main():
    print("\n" + "=" * 70)
    print("{evaluation_title}")
    print("=" * 70)

    evaluator = {EvaluatorClass}(model=get_model())
    logger.info("{EvaluatorClass} を初期化しました")

    experiment = Experiment(
        cases=EVAL_CASES,
        evaluators=[evaluator],
    )

    reports = experiment.run_evaluations(run_eval_task)

    report_path = os.path.join(_LOGS_DIR, "eval_{evaluation_name}_report.json")
    for report in reports:
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report.to_dict(), f, ensure_ascii=False, indent=2)
        logger.info("評価完了: レポート → %s", report_path)
        report.run_display()


if __name__ == "__main__":
    main()
```

---

## スケルトンコード（シングルターン評価 — ToolSelectionAccuracyEvaluator）

マルチターン版から以下の2箇所を変更してください。

### 変更1: import の差分

```python
# 変更前（マルチターン）
from helpers import (
    patch_human_approval_hook, {agent_factory}, run_actor_conversation,
    memory_exporter, get_model, create_invocation_state,
)
from strands_evals.evaluators import {EvaluatorClass}

# 変更後（シングルターン）— run_actor_conversation は不要
from helpers import (
    patch_human_approval_hook, {agent_factory},
    memory_exporter, get_model, create_invocation_state,
)
from strands_evals.evaluators import ToolSelectionAccuracyEvaluator
```

### 変更2: run_eval_task の差分

```python
def run_eval_task(case: Case) -> dict:
    """Experiment に渡す task 関数（シングルターン評価）。"""
    session_id = case.session_id
    logger.info("=== ケース '%s' 開始 (session: %s) ===", case.name, session_id)

    memory_exporter.clear()

    agent = {agent_factory}(session_id)
    state = create_invocation_state(session_id)

    # ---- 1ターンだけ送信（ツール選択の判定に十分）----
    result = agent(case.input, invocation_state=state.model_dump())
    response = str(result)

    logger.info("ケース '%s': response='%s'", case.name, response[:100])

    finished_spans = memory_exporter.get_finished_spans()
    mapper = StrandsInMemorySessionMapper()
    session = mapper.map_to_session(finished_spans, session_id=session_id)

    return {"output": response, "trajectory": session}
```

### 変更3: EVAL_CASES の metadata キー

```python
# シングルターン版では "goal" を "expected_tool" に変更する
Case(
    name="{case_name_1}",
    input="{user_input_1}",
    metadata={
        "task_description": "{task_description_1}",
        "expected_tool": "{expected_subagent_name}",  # ← "goal" から変更
    },
),
```

---

## カスタマイズガイド

1. **評価タイプの選択**: ルーティング精度の検証には「シングルターン（`ToolSelectionAccuracyEvaluator` + `expected_tool`）」を、エンドツーエンドの品質検証には「マルチターン（`GoalSuccessRateEvaluator` + `goal`）」を選ぶ。

2. **評価器の差し替え**: `{EvaluatorClass}` を目的の評価器クラスに置き換え、`metadata` のキーも対応して変更する（`"goal"` vs `"expected_tool"`）。

3. **テストケースの追加**: `EVAL_CASES` に `Case(...)` を追記する。`input` は会話の起点のみ記述する（2ターン目以降は ActorSimulator が LLM で自動生成）。`"goal"` / `"expected_tool"` の文字列が LLM-as-Judge の判定基準になるため、具体的に記述すること。

4. **エージェント関数の差し替え**: `{agent_factory}` を評価対象エージェントの生成関数名に変更する（`helpers.py` に実装が必要）。

5. **ログファイル名の変更**: `eval_{evaluation_name}.log` / `eval_{evaluation_name}_report.json` の `{evaluation_name}` 部分を実際のスクリプト名と一致させる。

6. **初期設定の順序を変えない**: `[1]UTF-8設定 → [2]sys.path → [3]load_dotenv → [4]patch_human_approval_hook → [5]ログ設定 → [6]warnings → [7]SDKログ抑制` の順序は `eval_common_system_design.md` §6.1 で規定された必須順序であり変更禁止。

7. **`memory_exporter.clear()` を省かない**: 各ケース実行前に必ず呼ぶ。省略すると前ケースのスパンが混入して評価結果が不正になる。
