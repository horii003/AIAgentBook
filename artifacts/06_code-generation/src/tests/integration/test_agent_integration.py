"""結合テスト: エージェント間連携の検証"""
import sys
import os
import json
import tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import pytest
from unittest.mock import MagicMock, patch
from openpyxl import Workbook
from strands import Agent


# ============================================================
# 1. TransportCalculatorInput ↔ calculate_transport_fare
# ============================================================
class TestDataModelAndTransportTool:
    """データモデルとツールの連携テスト"""

    def setup_method(self):
        """各テスト前にキャッシュをリセットする。"""
        import tools.transport_tools as tt
        tt._train_routes = [
            {"departure": "渋谷", "destination": "新宿", "fare": 200},
        ]
        tt._train_routes_loaded = True
        tt._fixed_fares = {"bus": 220, "taxi": 2000, "airplane": 50000}
        tt._fixed_fares_loaded = True

    def test_validated_input_to_calculate_fare(self):
        """TransportCalculatorInput でバリデーションした入力を calculate_transport_fare に渡して正常に計算できること"""
        from models.data_models import TransportCalculatorInput
        from tools.transport_tools import calculate_transport_fare

        # バリデーション
        validated = TransportCalculatorInput(
            departure="渋谷駅",  # 正規化される
            destination="新宿",
            transport_type="train",  # 正規化される
            travel_date="2026-01-15",
        )
        assert validated.departure == "渋谷"
        assert validated.transport_type == "電車"

        # ツール呼び出し
        ctx = MagicMock()
        ctx.invocation_state = {"applicant_name": "山田太郎", "application_date": "2026-01-15"}
        result = calculate_transport_fare.__wrapped__(
            departure=validated.departure,
            destination=validated.destination,
            transport_type=validated.transport_type,
            travel_date=validated.travel_date,
            tool_context=ctx,
        )
        assert result["success"] is True
        assert result["fare"] == 200


# ============================================================
# 2. ExpenseReportInput ↔ generate_expense_report
# ============================================================
class TestDataModelAndOutputTool:
    """データモデルとツールの連携テスト"""

    def test_validated_input_to_generate_expense_report(self, tmp_path):
        """ExpenseReportInput でバリデーションした入力を generate_expense_report に渡して正常にファイル生成できること"""
        from models.data_models import ExpenseReportInput
        from tools.output_generator import generate_expense_report
        import tools.output_generator as og

        # モックテンプレート作成
        wb = Workbook()
        template_path = str(tmp_path / "expense_template.xlsx")
        wb.save(template_path)
        output_dir = str(tmp_path / "output")

        original_template = og._EXPENSE_TEMPLATE_PATH
        original_output = og._OUTPUT_DIR
        og._EXPENSE_TEMPLATE_PATH = template_path
        og._OUTPUT_DIR = output_dir

        try:
            # バリデーション
            validated = ExpenseReportInput(items=[{
                "purchase_date": "2026-01-10",
                "store_name": "テスト店",
                "item_name": "ボールペン",
                "expense_category": "事務用品費",
                "amount": 500,
                "business_purpose": "業務用",
            }])
            assert len(validated.items) == 1

            # ツール呼び出し
            ctx = MagicMock()
            ctx.invocation_state = {"applicant_name": "山田太郎", "application_date": "2026-01-15"}
            result = generate_expense_report.__wrapped__(
                items=[item.model_dump() for item in validated.items],
                tool_context=ctx,
            )
            assert result["success"] is True
            assert result["file_path"] is not None
        finally:
            og._EXPENSE_TEMPLATE_PATH = original_template
            og._OUTPUT_DIR = original_output


# ============================================================
# 3. LoopControlHook ↔ ErrorHandler
# ============================================================
class TestLoopControlHookAndErrorHandler:
    """LoopControlHook と ErrorHandler の連携テスト"""

    def test_loop_limit_error_raised_and_handled(self):
        """LoopControlHook が上限到達時に LoopLimitError を raise し、ErrorHandler が文字列を返すこと"""
        from handlers.loop_control_hook import LoopControlHook
        from handlers.error_handler import LoopLimitError, ErrorHandler

        hook = LoopControlHook(max_iterations=3, agent_name="テストエージェント")
        event = MagicMock()
        event.exception = None

        # 3回インクリメントして上限到達
        hook.on_after_model_call(event)
        hook.on_after_model_call(event)
        with pytest.raises(LoopLimitError) as exc_info:
            hook.on_after_model_call(event)

        # ErrorHandler でメッセージ生成
        msg = ErrorHandler.handle_loop_limit_error(exc_info.value)
        assert isinstance(msg, str)
        assert len(msg) > 0


# ============================================================
# 4. HumanApprovalHook ↔ generate_expense_report
# ============================================================
class TestHumanApprovalHookAndOutputTool:
    """HumanApprovalHook と出力ツールの連携テスト"""

    def test_approved_true_does_not_cancel_tool(self):
        """HumanApprovalHook が承認コールバック (True, '') の場合にツールをキャンセルしないこと"""
        from handlers.human_approval_hook import HumanApprovalHook

        callback = MagicMock(return_value=(True, ""))
        hook = HumanApprovalHook(approval_callback=callback)

        event = MagicMock()
        event.tool_use = {"name": "generate_expense_report", "input": {}}
        event.cancel_tool = False

        hook._on_before_tool_call(event)
        assert event.cancel_tool is False

    def test_approved_false_cancel_sets_cancel_tool(self):
        """HumanApprovalHook が承認コールバック (False, 'CANCEL') の場合に event.cancel_tool が設定されること"""
        from handlers.human_approval_hook import HumanApprovalHook

        callback = MagicMock(return_value=(False, "CANCEL"))
        hook = HumanApprovalHook(approval_callback=callback)

        event = MagicMock()
        event.tool_use = {"name": "generate_transport_report", "input": {}}
        event.cancel_tool = False

        hook._on_before_tool_call(event)
        assert isinstance(event.cancel_tool, str)
        assert len(event.cancel_tool) > 0


# ============================================================
# 5. SessionManagerFactory ↔ Agent
# ============================================================
class TestSessionManagerAndAgent:
    """セッション管理とエージェントの連携テスト"""

    @patch("agents.base_agent.ModelConfig.get_model")
    def test_session_manager_passed_to_agent(self, mock_model, tmp_path):
        """SessionManagerFactory.create_session_manager() で生成したセッションマネージャーが Agent に渡せること"""
        from session.session_manager import SessionManagerFactory
        from agents.base_agent import create_specialist_agent

        mock_model.return_value = MagicMock()
        SessionManagerFactory._storage_dir = str(tmp_path / "sessions")

        agent = create_specialist_agent(
            session_id="test_session",
            system_prompt="テストプロンプト",
            tools=[],
            agent_name="テストエージェント",
            window_size=15,
            max_iterations=10,
            max_attempts=6,
            initial_delay=4,
            max_delay=240,
        )
        assert isinstance(agent, Agent)
        SessionManagerFactory._storage_dir = None


# ============================================================
# 6. calculate_deadline ↔ get_transport_system_prompt
# ============================================================
class TestDeadlineAndPrompt:
    """期限計算とプロンプト生成の連携テスト"""

    def test_deadline_passed_to_transport_prompt(self):
        """calculate_deadline() で計算した期限が get_transport_system_prompt() に正しく渡されること"""
        from agents.base_agent import calculate_deadline
        from prompt.prompt_specialist_transport import get_transport_system_prompt
        from knowledge.transport_policies import get_transport_policies

        deadline = calculate_deadline("2026-01-15", 3)
        assert deadline == "2025-10-15"

        prompt = get_transport_system_prompt(
            applicant_name="山田太郎",
            application_date="2026-01-15",
            deadline_date=deadline,
            transport_policies=get_transport_policies(3, 10000),
        )
        assert "2025-10-15" in prompt


# ============================================================
# 7. settings ↔ get_transport_policies
# ============================================================
class TestSettingsAndPolicies:
    """設定値とポリシー生成の連携テスト"""

    def test_settings_transport_deadline_months_passed_to_policies(self):
        """settings.transport.deadline_months が get_transport_policies() の引数として正しく渡されること"""
        from config.settings import settings
        from knowledge.transport_policies import get_transport_policies

        policies = get_transport_policies(
            deadline_months=settings.transport.deadline_months,
            approval_threshold=settings.transport.approval_threshold,
        )
        assert str(settings.transport.deadline_months) in policies
        assert f"{settings.transport.approval_threshold:,}" in policies
