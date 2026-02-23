"""ToolSelectionAccuracyEvaluator による受付エージェントのツール選択評価

受付エージェント（reception_agent）が、ユーザーの要求に応じて
適切なツール（transportation_expense_agent / receipt_expense_agent）を選択しているかを
各ツール呼び出し単位で二値（Yes=1.0 / No=0.0）評価します。

評価レベル: TOOL_LEVEL
  - 会話中の各ツール呼び出しを個別に評価
  - そのタイミングでそのツールを選択することが妥当かを LLM-as-Judge で判定

実行方法:
    python evals/eval_tool_selection.py
"""

import sys
import os
import json
import logging
import warnings
from dotenv import load_dotenv
from helpers import (
    patch_human_approval_hook, create_reception_agent,
    memory_exporter, get_model, create_invocation_state,
)
from strands_evals import Case, Experiment
from strands_evals.evaluators import ToolSelectionAccuracyEvaluator
from strands_evals.mappers import StrandsInMemorySessionMapper

# ---- 初期設定 ----
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv()
patch_human_approval_hook()

# ---- ログ設定 ----
_LOGS_DIR = os.path.join("evals", "logs")
os.makedirs(_LOGS_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(
            os.path.join(_LOGS_DIR, "eval_tool_selection.log"),
            encoding="utf-8",
        ),
    ],
)
logger = logging.getLogger(__name__)
warnings.filterwarnings("ignore")

# strands SDK のログを抑制（評価時は不要なため）
logging.getLogger("strands").setLevel(logging.WARNING)
logging.getLogger("strands.event_loop.event_loop").setLevel(logging.CRITICAL)


# ================================================================
# テストケース定義（Case オブジェクト）
# ================================================================

EVAL_CASES = [
    Case(
        name="travel_tooltest",
        input="交通費の申請をお願いします。2026年2月22日に東京から渋谷まで電車で移動しました。",
        metadata={
            "task_description": "交通費精算を依頼した際に、適切にtransportation_expense_agentを選択するかテストする",
            "expected_tool": "transportation_expense_agent",
        },
    ),
    Case(
        name="receipt_expense_tooltest",
        input="先日購入した書籍の領収書があります。",
        metadata={
            "task_description": "領収書精算を依頼した際に、適切にreceipt_expense_agentを選択するかテストする",
            "expected_tool": "receipt_expense_agent",
        },
    ),
]


# ================================================================
# タスク関数（Experiment に渡す）
# ================================================================

def run_eval_task(case: Case) -> dict:
    """Experiment に渡す task 関数。

    Case を受け取り、1ターンだけエージェントにメッセージを送信し、
    受付エージェントのツール選択をテレメトリから記録する。

    Args:
        case: strands_evals Case オブジェクト

    Returns:
        dict: {"output": 最終応答, "trajectory": Session オブジェクト}
    """
    session_id = case.session_id
    logger.info("=== ケース '%s' 開始 (session: %s) ===", case.name, session_id)

    # スパンをリセット（前のケースのスパンが混入しないようにする）
    memory_exporter.clear()

    # ---- エージェント作成（trace_attributes 付き） ----
    agent = create_reception_agent(session_id)

    # ---- InvocationState ----
    state = create_invocation_state(session_id)

    # ---- 1ターンだけ送信（ツール選択の判定に十分） ----
    result = agent(case.input, invocation_state=state.model_dump())
    response = str(result)

    logger.info("ケース '%s': response='%s'", case.name, response[:100])

    # ---- テレメトリスパンから Session を自動構築 ----
    finished_spans = memory_exporter.get_finished_spans()
    mapper = StrandsInMemorySessionMapper()
    session = mapper.map_to_session(finished_spans, session_id=session_id)

    return {"output": response, "trajectory": session}


# ================================================================
# メイン
# ================================================================

def main():
    print("\n" + "=" * 70)
    print("ToolSelectionAccuracyEvaluator - 受付エージェントのツール選択評価")
    print("=" * 70)

    # ---- 評価器の初期化 ----
    evaluator = ToolSelectionAccuracyEvaluator(model=get_model())
    logger.info("ToolSelectionAccuracyEvaluator を初期化しました")

    # ---- Experiment の構成と実行 ----
    experiment = Experiment(
        cases=EVAL_CASES,
        evaluators=[evaluator],
    )

    reports = experiment.run_evaluations(run_eval_task)

    # ---- 結果表示・保存 ----
    report_path = os.path.join(_LOGS_DIR, "eval_tool_selection_report.json")
    for report in reports:
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report.to_dict(), f, ensure_ascii=False, indent=2)
        logger.info("評価完了: レポート → %s", report_path)
        report.run_display()


if __name__ == "__main__":
    main()
