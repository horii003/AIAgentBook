"""ツール選択精度評価（MET-001）

AG-001 が申請内容に応じて transport_agent / expense_agent を正しく選択するかを評価する。

評価レベル: TOOL_LEVEL（出力レベル）
実行方式: シングルターン
実行方法: python evals/eval_tool_selection.py
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
    patch_human_approval_hook,
    create_orchestrator_agent,
    memory_exporter,
    get_model,
    create_invocation_state,
)

patch_human_approval_hook()

from strands_evals import Case, Experiment
from strands_evals.evaluators import ToolSelectionAccuracyEvaluator
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
            os.path.join(_LOGS_DIR, "eval_tool_selection.log"),
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
        name="tool_selection_transport_basic",
        input="昨日、営業訪問のため渋谷から新宿まで電車で移動しました（運賃170円）。交通費を精算したいです。",
        metadata={
            "task_description": "交通費精算申請に対して transport_agent が選択されることを確認する",
            "expected_tool": "transport_agent",
        },
    ),
    Case(
        name="tool_selection_expense_stationery",
        input="業務用のボールペンとノートを購入しました。領収書があります。経費精算をお願いします。",
        metadata={
            "task_description": "経費精算申請（事務用品費）に対して expense_agent が選択されることを確認する",
            "expected_tool": "expense_agent",
        },
    ),
    Case(
        name="tool_selection_expense_accommodation",
        input="先週の出張で東京から横浜へ移動し（運賃480円）、ホテルに宿泊しました。宿泊費の経費精算をお願いします。",
        metadata={
            "task_description": "経費精算申請（宿泊費）に対して expense_agent が選択されることを確認する",
            "expected_tool": "expense_agent",
        },
    ),
]


# ================================================================
# タスク関数
# ================================================================

def run_eval_task(case: Case) -> dict:
    """Experiment に渡す task 関数（シングルターン評価）。"""
    session_id = case.session_id or case.name
    logger.info("ケース開始: %s (session_id=%s)", case.name, session_id)

    # [1] 前ケースのスパン混入防止
    memory_exporter.clear()

    # [2] エージェント生成
    agent = create_orchestrator_agent(session_id)

    # [3] 状態生成
    invocation_state = create_invocation_state(session_id)

    # [4] 1ターン送信
    try:
        result = agent(case.input, invocation_state=invocation_state)
        response = str(result)
        logger.info("エージェント応答: %s", response[:200])
    except Exception as e:
        logger.error("エージェント例外: %s", e)
        response = ""

    # [5] スパン収集 → Session 構築
    spans = list(memory_exporter.get_finished_spans())
    session = StrandsInMemorySessionMapper().map_to_session(spans, session_id=session_id)

    logger.info("ケース完了: %s", case.name)
    return {"output": response, "trajectory": session}


# ================================================================
# メイン
# ================================================================

def main():
    """評価実験を実行し、レポートを保存する。"""
    logger.info("eval_tool_selection 開始")

    # [1] 評価器生成
    evaluator = ToolSelectionAccuracyEvaluator(model=get_model())

    # [2] 実験構成
    experiment = Experiment(cases=EVAL_CASES, evaluators=[evaluator])

    # [3] 評価実行
    reports = experiment.run_evaluations(run_eval_task)

    # [4] レポート保存
    report_path = os.path.join(_REPORTS_DIR, "eval_tool_selection_report.json")
    for report in reports:
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report.to_dict(), f, ensure_ascii=False, indent=2)
        logger.info("レポート保存: %s", report_path)

        # [5] コンソール表示
        report.run_display()

    logger.info("eval_tool_selection 完了")


if __name__ == "__main__":
    main()
