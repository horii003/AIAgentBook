"""申請種別ルーティング精度評価

評価レベル: TURN_LEVEL
  - 申請受付窓口エージェント（AG-001）が入力テキストから正しい専門エージェントを選択するかを検証
  - ToolSelectionAccuracyEvaluator が1ターンのツール選択を LLM-as-Judge で判定

実行方法:
    python evals/eval_routing_accuracy.py
"""

import json
import logging
import os
import sys
import warnings

from dotenv import load_dotenv

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
from helpers import (
    create_invocation_state,
    create_orchestrator_agent,
    get_model,
    memory_exporter,
    patch_human_approval_hook,
)

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
            os.path.join(_LOGS_DIR, "eval_routing_accuracy.log"),
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

from strands_evals import Case, Experiment
from strands_evals.evaluators import ToolSelectionAccuracyEvaluator
from strands_evals.mappers import StrandsInMemorySessionMapper

# ================================================================
# テストケース定義（Case オブジェクト）
# ================================================================

EVAL_CASES = [
    Case(
        name="交通費精算申請の振り分け",
        input="電車で渋谷から新宿に移動した交通費を精算したい",
        metadata={
            "task_description": "交通費精算申請の入力に対してtransport_agentを呼び出すこと",
            "expected_tool": "transport_agent",
        },
    ),
    Case(
        name="経費精算申請の振り分け",
        input="文房具を購入した領収書を精算したい",
        metadata={
            "task_description": "経費精算申請の入力に対してexpense_agentを呼び出すこと",
            "expected_tool": "expense_agent",
        },
    ),
    Case(
        name="判断不能時の選択肢提示",
        input="精算したいものがある",
        metadata={
            "task_description": "曖昧な入力に対して選択肢を提示すること",
            "expected_tool": "none",
        },
    ),
    Case(
        name="対象外申請のエスカレーション",
        input="有給休暇を申請したい",
        metadata={
            "task_description": "対象外の申請に対してエスカレーション案内を表示すること",
            "expected_tool": "none",
        },
    ),
]


# ================================================================
# タスク関数（Experiment に渡す）
# ================================================================


def run_eval_task(case: Case) -> dict:
    """Experiment に渡す task 関数（シングルターン評価）。

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
    agent_wrapper = create_orchestrator_agent(session_id)
    agent = agent_wrapper._agent

    # ---- InvocationState ----
    state = create_invocation_state(session_id)

    # ---- シングルターン実行 ----
    result = agent(case.input, invocation_state=state)
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
    print("申請種別ルーティング精度評価")
    print("=" * 70)

    evaluator = ToolSelectionAccuracyEvaluator(model=get_model())
    logger.info("ToolSelectionAccuracyEvaluator を初期化しました")

    experiment = Experiment(
        cases=EVAL_CASES,
        evaluators=[evaluator],
    )

    reports = experiment.run_evaluations(run_eval_task)

    report_path = os.path.join(_LOGS_DIR, "eval_routing_accuracy_report.json")
    for report in reports:
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report.to_dict(), f, ensure_ascii=False, indent=2)
        logger.info("評価完了: レポート → %s", report_path)
        report.run_display()


if __name__ == "__main__":
    main()
