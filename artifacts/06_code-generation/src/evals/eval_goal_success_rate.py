"""有用性評価（MET-002: 経費申請ゴール達成率）

AG-001→AG-002/AG-003 の連携による Excel 申請書生成のゴール達成を
GoalSuccessRateEvaluator でマルチターン評価する。

評価レベル: SESSION_LEVEL
実行方法: python evals/eval_goal_success_rate.py
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
    run_actor_conversation,
    memory_exporter,
    get_model,
    create_invocation_state,
)

patch_human_approval_hook()

from strands_evals import Case, Experiment
from strands_evals.evaluators import GoalSuccessRateEvaluator
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
            os.path.join(_LOGS_DIR, "eval_goal_success_rate.log"),
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
            "task_description": "東京→新宿の電車移動（200円）の交通費精算申請書が正しく生成されること",
            "goal": "申請者名「田中太郎」、移動日「2026-05-18」、出発地「東京」、目的地「新宿」、交通手段「電車」、交通費「200円」、業務目的「顧客訪問」が記載された交通費精算申請書（Excel）が生成されること",
        },
    ),
    Case(
        name="transport_taxi_business_trip",
        input="申請者は鈴木花子です。出張でタクシーを使いました。2026-05-15に品川から渋谷まで移動しました。業務目的は取引先訪問です。交通費の精算をお願いします。",
        metadata={
            "task_description": "タクシー移動（品川→渋谷）の交通費精算申請書が正しく生成されること",
            "goal": "申請者名「鈴木花子」、移動日「2026-05-15」、出発地「品川」、目的地「渋谷」、交通手段「タクシー」、業務目的「取引先訪問」が記載された交通費精算申請書（Excel）が生成されること",
        },
    ),
    Case(
        name="expense_office_supplies",
        input="申請者は山田次郎です。2026-05-10に東京文具店でボールペンとノートを3,000円で購入しました。業務目的は業務用消耗品の補充です。経費申請をしたいです。",
        metadata={
            "task_description": "事務用品購入の経費精算申請書が正しく生成されること",
            "goal": "申請者名「山田次郎」、購入日「2026-05-10」、店舗名「東京文具店」、品目「ボールペン・ノート」、経費区分「事務用品費」、金額「3,000円」、業務目的「業務用消耗品の補充」が記載された経費精算申請書（Excel）が生成されること",
        },
    ),
]


# ================================================================
# タスク関数
# ================================================================

def run_eval_task(case: Case) -> dict:
    """Experiment に渡す task 関数（マルチターン評価）。

    Args:
        case: 評価ケース

    Returns:
        dict: {"output": str, "trajectory": Session}
    """
    # 前ケースのスパン混入防止（ケース開始時に1回のみ）
    memory_exporter.clear()

    # エージェント生成
    agent = create_orchestrator_agent(session_id=case.session_id)

    # 状態生成
    invocation_state_dict = create_invocation_state(session_id=case.session_id)

    # マルチターン会話実行
    # run_actor_conversation 内では memory_exporter.clear() を呼ばない（全ターンのスパンを蓄積）
    turns = run_actor_conversation(
        agent=agent,
        case=case,
        invocation_state_dict=invocation_state_dict,
        max_turns=10,
    )

    # 最終応答を取得
    final_response = turns[-1]["agent_response"] if turns else ""

    # 全ターンのスパンをまとめて収集 → Session 構築
    spans = list(memory_exporter.get_finished_spans())
    session = StrandsInMemorySessionMapper().map_to_session(spans, session_id=case.session_id)

    return {"output": final_response, "trajectory": session}


# ================================================================
# メイン
# ================================================================

def main():
    """評価実験を実行し、レポートを保存する。"""
    logger.info("有用性評価（MET-002）を開始します")

    # 評価器生成
    evaluator = GoalSuccessRateEvaluator(model=get_model())

    # 実験構成
    experiment = Experiment(cases=EVAL_CASES, evaluators=[evaluator])

    # 評価実行
    reports = experiment.run_evaluations(run_eval_task)

    # レポート保存
    report_path = os.path.join(_REPORTS_DIR, "eval_goal_success_rate_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(reports[0].to_dict(), f, ensure_ascii=False, indent=2)
    logger.info("レポートを保存しました: %s", report_path)

    # コンソール表示
    reports[0].run_display()


if __name__ == "__main__":
    main()
