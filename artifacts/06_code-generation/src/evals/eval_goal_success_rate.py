"""申請書作成ゴール達成率評価（MET-002）

AG-001→AG-003/AG-002 の連携により Excel 申請書が正しいデータで生成されることを評価する。

評価レベル: SESSION_LEVEL
実行方式: マルチターン（ActorSimulator）
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
        name="goal_transport_single_route",
        input="昨日、営業訪問のため渋谷から新宿まで電車で移動しました（運賃170円）。交通費精算をお願いします。",
        metadata={
            "task_description": "交通費精算申請書（Excel）が正しいデータで生成されることを確認する",
            "goal": (
                "交通費精算申請書ファイルが output/ に生成され、"
                "申請者名・移動日・出発地（渋谷）・目的地（新宿）・交通手段（電車）・"
                "交通費（170円）・業務目的が正しく記載されていること"
            ),
        },
    ),
    Case(
        name="goal_expense_stationery",
        input="先週、業務用の文房具（ボールペン3本、ノート2冊）を購入しました。合計1,500円です。経費精算をお願いします。",
        metadata={
            "task_description": "経費精算申請書（Excel）が正しいデータで生成されることを確認する",
            "goal": (
                "経費精算申請書ファイルが output/ に生成され、"
                "申請者名・購入日・品目・経費区分（事務用品費）・金額（1,500円）・"
                "業務目的・合計金額が正しく記載されていること"
            ),
        },
    ),
    Case(
        name="goal_transport_multi_routes",
        input="今週月曜日に渋谷→新宿（電車・170円）、火曜日に新宿→池袋（電車・170円）の2区間を移動しました。交通費精算をお願いします。",
        metadata={
            "task_description": "複数区間の交通費精算申請書が正しいデータで生成されることを確認する",
            "goal": (
                "交通費精算申請書ファイルが output/ に生成され、"
                "2区間（渋谷→新宿170円、新宿→池袋170円）の移動明細・"
                "合計金額（340円）が正しく記載されていること"
            ),
        },
    ),
]


# ================================================================
# タスク関数
# ================================================================

def run_eval_task(case: Case) -> dict:
    """Experiment に渡す task 関数（マルチターン評価）。"""
    session_id = case.session_id or case.name
    logger.info("ケース開始: %s (session_id=%s)", case.name, session_id)

    # [1] 前ケースのスパン混入防止
    memory_exporter.clear()

    # [2] エージェント生成
    agent = create_orchestrator_agent(session_id)

    # [3] 状態生成
    invocation_state = create_invocation_state(session_id)

    # [4] マルチターン会話実行（各ターン内で memory_exporter.clear() 済み）
    turns = run_actor_conversation(
        agent=agent,
        case=case,
        invocation_state_dict=invocation_state,
        max_turns=30,
    )

    final_response = turns[-1]["agent_response"] if turns else ""
    logger.info("会話完了: %d ターン, ケース=%s", len(turns), case.name)

    # [5] スパン収集 → Session 構築
    spans = list(memory_exporter.get_finished_spans())
    session = StrandsInMemorySessionMapper().map_to_session(spans, session_id=session_id)

    logger.info("ケース完了: %s", case.name)
    return {"output": final_response, "trajectory": session}


# ================================================================
# メイン
# ================================================================

def main():
    """評価実験を実行し、レポートを保存する。"""
    logger.info("eval_goal_success_rate 開始")

    # [1] 評価器生成
    evaluator = GoalSuccessRateEvaluator(model=get_model())

    # [2] 実験構成
    experiment = Experiment(cases=EVAL_CASES, evaluators=[evaluator])

    # [3] 評価実行
    reports = experiment.run_evaluations(run_eval_task)

    # [4] レポート保存
    report_path = os.path.join(_REPORTS_DIR, "eval_goal_success_rate_report.json")
    for report in reports:
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report.to_dict(), f, ensure_ascii=False, indent=2)
        logger.info("レポート保存: %s", report_path)

        # [5] コンソール表示
        report.run_display()

    logger.info("eval_goal_success_rate 完了")


if __name__ == "__main__":
    main()
