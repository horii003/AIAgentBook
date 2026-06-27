"""ゴール達成率評価

オーケストレーターエージェントがマルチターン会話を通じて経費精算申請書の
生成ゴールを達成できるかを評価する（マルチターン）。

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
    create_eval_agent,
    run_actor_conversation,
    memory_exporter,
    get_model,
    create_invocation_state,
)

# エージェントモジュールのインポート前にパッチを適用
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
        name="GS-01_交通費申請_電車",
        input="先週、東京から新宿まで電車で移動しました。交通費を精算したいです。",
        metadata={
            "task_description": "交通費精算の一連フローが完了することを検証する（AG-001→AG-002連携）",
            "goal": "申請者名・移動日・出発地・目的地・交通手段・交通費・業務目的が記載された交通費精算申請書（Excel）が正常に生成されること",
        },
    ),
    Case(
        name="GS-02_交通費申請_タクシー",
        input="昨日、客先訪問のためタクシーを利用しました。交通費の申請をお願いします。",
        metadata={
            "task_description": "タクシー利用の交通費精算フローが完了することを検証する（AG-001→AG-002連携）",
            "goal": "申請者名・移動日・出発地・目的地・交通手段・交通費・業務目的が記載された交通費精算申請書（Excel）が正常に生成されること",
        },
    ),
    Case(
        name="GS-03_経費申請_備品購入",
        input="業務用のノートとボールペンを購入しました。2026年5月20日に文具堂で1,500円でした。経費精算をお願いします。",
        metadata={
            "task_description": "経費精算の一連フローが完了することを検証する（AG-001→AG-003連携）",
            "goal": "申請者名・購入日・品目・経費区分・金額・業務目的・合計金額が記載された経費精算申請書（Excel）が正常に生成されること",
        },
    ),
        Case(
        name="GS-04_交通費申請_電車",
        input="先週、豊洲から新宿まで電車で移動しました。交通費を精算したいです。",
        metadata={
            "task_description": "交通費精算の一連フローが完了することを検証する（AG-001→AG-002連携）",
            "goal": "申請者名・移動日・出発地・目的地・交通手段・交通費・業務目的が記載された交通費精算申請書（Excel）が正常に生成されること",
        },
    ),
        Case(
        name="GS-05_交通費申請_電車",
        input="先週、豊洲から練馬まで電車で移動しました。交通費を精算したいです。",
        metadata={
            "task_description": "交通費精算の一連フローが完了することを検証する（AG-001→AG-002連携）",
            "goal": "申請者名・移動日・出発地・目的地・交通手段・交通費・業務目的が記載された交通費精算申請書（Excel）が正常に生成されること",
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
        dict: {"output": エージェント応答, "trajectory": Sessionオブジェクト}
    """
    # 1. 前ケースのスパン混入防止（ケース開始時に1回のみ）
    memory_exporter.clear()

    # 2. エージェント生成
    session_id = case.session_id or f"eval_gs_{case.name}"
    invocation_state = create_invocation_state(session_id=session_id)
    agent = create_eval_agent(session_id=session_id)

    # 3. マルチターン会話実行（内部でmemory_exporter.clear()を呼ばない）
    final_response = run_actor_conversation(
        agent=agent,
        case=case,
        invocation_state_dict=invocation_state,
        max_turns=10,
    )

    # 4. スパン収集（ループ完了後にまとめて）
    spans = list(memory_exporter.get_finished_spans())

    # 5. Session構築
    session = StrandsInMemorySessionMapper().map_to_session(
        spans, session_id=session_id
    )

    # 6. 結果返却
    return {"output": final_response, "trajectory": session}


# ================================================================
# メイン
# ================================================================

def main():
    """評価実験を実行し、レポートを保存する。"""
    logger.info("ゴール達成率評価を開始します")

    evaluator = GoalSuccessRateEvaluator(model=get_model())
    experiment = Experiment(cases=EVAL_CASES, evaluators=[evaluator])

    reports = experiment.run_evaluations(run_eval_task)

    # レポートをJSON保存
    report_path = os.path.join(_REPORTS_DIR, "eval_goal_success_rate_report.json")
    report_data = []
    for report in reports:
        report_data.append(report.to_dict())

    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)

    logger.info("レポートを保存しました: %s", report_path)

    # コンソール表示
    for report in reports:
        report.run_display()


if __name__ == "__main__":
    main()
