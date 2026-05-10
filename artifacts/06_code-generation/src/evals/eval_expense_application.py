"""経費精算申請シナリオ評価スクリプト

AG-001→AG-003の連携フローで経費精算申請書が正常に生成されるかを評価する。
EV-003（申請書生成完全性）・EV-005（業務ルール遵守）・EV-010（経費区分判断正確性）に対応。

評価レベル: SESSION_LEVEL（マルチターン評価）
  - StrandsEvalsTelemetry でエージェントの実行スパンを自動キャプチャ
  - StrandsInMemorySessionMapper でスパンから Session を自動構築
  - GoalSuccessRateEvaluator が全ターン・全ツール呼び出しを LLM-as-Judge で判定

実行方法:
    python evals/eval_expense_application.py
"""

import sys
import os
import json
import logging
import warnings
from dotenv import load_dotenv
from helpers import (
    patch_human_approval_hook, create_orchestrator_agent, run_actor_conversation,
    memory_exporter, get_model, create_invocation_state,
)
from strands_evals import Case, Experiment
from strands_evals.evaluators import GoalSuccessRateEvaluator
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
            os.path.join(_LOGS_DIR, "eval_expense_application.log"),
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
    # TC-E2E-010: 経費精算申請の完全フロー
    Case(
        name="経費精算申請_完全フロー",
        input="備品を購入したので経費申請したいです",
        metadata={
            "task_description": "経費精算申請の完全フロー（経費情報収集→経費区分判断・確認→申請書生成）が正常に動作すること",
            "goal": "output/経費精算申請書_{timestamp}.xlsxが生成され、申請書生成完了メッセージが返されること",
        },
    ),
    # TC-E2E-011: 経費区分確認フロー
    Case(
        name="経費区分確認_事務用品",
        input="ノートを購入したので経費申請したいです",
        metadata={
            "task_description": "品目から経費区分を自動判断し、必ずユーザーへ確認を求めること（BRL-14）",
            "goal": "経費区分の候補（事務用品費）が提示され、ユーザーへの確認が求められること",
        },
    ),
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
    agent = create_orchestrator_agent(session_id)

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
    print("経費精算申請シナリオ評価（GoalSuccessRateEvaluator）")
    print("=" * 70)

    evaluator = GoalSuccessRateEvaluator(model=get_model())
    logger.info("GoalSuccessRateEvaluator を初期化しました")

    experiment = Experiment(
        cases=EVAL_CASES,
        evaluators=[evaluator],
    )

    reports = experiment.run_evaluations(run_eval_task)

    report_path = os.path.join(_LOGS_DIR, "eval_expense_application_report.json")
    for report in reports:
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report.to_dict(), f, ensure_ascii=False, indent=2)
        logger.info("評価完了: レポート → %s", report_path)
        report.run_display()


if __name__ == "__main__":
    main()
