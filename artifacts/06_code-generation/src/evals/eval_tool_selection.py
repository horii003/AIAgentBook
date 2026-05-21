"""ツール利用の適切性評価（MET-001: 申請種別判断正確率）

AG-001 が申請種別に応じて transportation_expense_agent / general_expense_agent を
正しく選択することを ToolSelectionAccuracyEvaluator で評価する。

評価レベル: TOOL_LEVEL
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
        name="transport_train_tokyo_shinjuku",
        input="申請者は田中太郎です。2026-05-18に東京から新宿まで電車で移動しました。業務目的は顧客訪問です。交通費を申請したいです。",
        metadata={
            "task_description": "電車移動の交通費精算申請として transportation_expense_agent が選択されること",
            "expected_tool": "transportation_expense_agent",
        },
    ),
    Case(
        name="transport_taxi_business_trip",
        input="申請者は鈴木花子です。出張でタクシーを使いました。2026-05-15に品川から渋谷まで移動しました。業務目的は取引先訪問です。交通費の精算をお願いします。",
        metadata={
            "task_description": "タクシー移動の交通費精算申請として transportation_expense_agent が選択されること",
            "expected_tool": "transportation_expense_agent",
        },
    ),
    Case(
        name="expense_office_supplies",
        input="申請者は山田次郎です。2026-05-10に東京文具店でボールペンとノートを3,000円で購入しました。業務目的は業務用消耗品の補充です。経費申請をしたいです。",
        metadata={
            "task_description": "事務用品購入の経費精算申請として general_expense_agent が選択されること",
            "expected_tool": "general_expense_agent",
        },
    ),
]


# ================================================================
# タスク関数
# ================================================================

def run_eval_task(case: Case) -> dict:
    """Experiment に渡す task 関数（シングルターン評価）。

    Args:
        case: 評価ケース

    Returns:
        dict: {"output": str, "trajectory": Session}
    """
    # 前ケースのスパン混入防止（必須）
    memory_exporter.clear()

    # エージェント生成
    agent = create_orchestrator_agent(session_id=case.session_id)

    # 状態生成
    invocation_state_dict = create_invocation_state(session_id=case.session_id)

    # 1ターン送信
    response = agent(case.input, invocation_state=invocation_state_dict)
    response_str = str(response)

    # スパン収集 → Session 構築
    spans = list(memory_exporter.get_finished_spans())
    session = StrandsInMemorySessionMapper().map_to_session(spans, session_id=case.session_id)

    return {"output": response_str, "trajectory": session}


# ================================================================
# メイン
# ================================================================

def main():
    """評価実験を実行し、レポートを保存する。"""
    logger.info("ツール利用の適切性評価（MET-001）を開始します")

    # 評価器生成
    evaluator = ToolSelectionAccuracyEvaluator(model=get_model())

    # 実験構成
    experiment = Experiment(cases=EVAL_CASES, evaluators=[evaluator])

    # 評価実行
    reports = experiment.run_evaluations(run_eval_task)

    # レポート保存
    report_path = os.path.join(_REPORTS_DIR, "eval_tool_selection_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(reports[0].to_dict(), f, ensure_ascii=False, indent=2)
    logger.info("レポートを保存しました: %s", report_path)

    # コンソール表示
    reports[0].run_display()


if __name__ == "__main__":
    main()
