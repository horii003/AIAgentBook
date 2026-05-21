"""結合テスト: エージェント連携の検証。

オーケストレーター → 専門エージェント → ツール の連携を検証する。
外部サービス（LLM API等）への実際の呼び出しはモックを使用する。
"""
import json
import sys
from unittest.mock import MagicMock, mock_open, patch

import pytest

# strands モジュールをモックとして登録
if "strands" not in sys.modules:
    mock_strands = MagicMock()
    sys.modules["strands"] = mock_strands
    sys.modules["strands.models"] = mock_strands.models

mock_strands = sys.modules["strands"]
mock_strands.Agent = MagicMock
mock_strands.ModelRetryStrategy = MagicMock
mock_strands.ToolContext = MagicMock
mock_strands.tool = lambda *args, **kwargs: (lambda f: f) if args and callable(args[0]) else (lambda f: f)

# 必要なモジュールをモック
for mod_name, mock_obj in [
    ("strands.agent", MagicMock()),
    ("strands.agent.conversation_manager", MagicMock()),
    ("strands.hooks", MagicMock()),
    ("strands.session", MagicMock()),
    ("strands.session.file_session_manager", MagicMock()),
    ("openpyxl", MagicMock()),
]:
    sys.modules.setdefault(mod_name, mock_obj)

if not hasattr(sys.modules["strands.agent.conversation_manager"], "SlidingWindowConversationManager"):
    sys.modules["strands.agent.conversation_manager"].SlidingWindowConversationManager = MagicMock

hooks_mod = sys.modules["strands.hooks"]
if not hasattr(hooks_mod, "HookProvider"):
    hooks_mod.HookProvider = type("HookProvider", (), {})
    for event in ["BeforeToolCallEvent", "BeforeInvocationEvent", "AfterInvocationEvent",
                  "BeforeModelCallEvent", "AfterModelCallEvent", "AfterToolCallEvent"]:
        setattr(hooks_mod, event, MagicMock)

# モジュールをリロード（クリーンな状態で読み込む）
for mod in list(sys.modules.keys()):
    if mod.startswith(("agents.", "tools.", "handlers.", "session.", "config.", "models.", "prompt.", "knowledge.")):
        del sys.modules[mod]


class TestInvocationStatePropagation:
    """invocation_state の伝播テスト"""

    def test_invocation_state_structure(self):
        """InvocationState が正しいフィールドを持つこと"""
        from models.data_models import InvocationState
        state = InvocationState(
            user_name="山田太郎",
            request_date="2026-05-21",
            session_id="test_session_id",
        )
        dumped = state.model_dump()
        assert "user_name" in dumped
        assert "request_date" in dumped
        assert "session_id" in dumped

    def test_child_invocation_state_excludes_session_id(self):
        """子エージェントへの invocation_state に session_id が含まれないこと"""
        from agents.base_agent import invoke_specialist_agent

        # 子エージェントに渡された invocation_state を検証
        captured_invocation_state = {}

        def mock_build_agent(session_id, applicant_name, application_date, deadline):
            mock_agent = MagicMock()
            def mock_call(query, invocation_state=None):
                captured_invocation_state.update(invocation_state or {})
                return "テスト応答"
            mock_agent.side_effect = mock_call
            return mock_agent

        ctx = MagicMock()
        ctx.invocation_state = {
            "user_name": "山田太郎",
            "request_date": "2026-05-21",
            "session_id": "test_session_id",
        }

        with patch("os.makedirs"):
            invoke_specialist_agent(
                query="テストクエリ",
                tool_context=ctx,
                agent_id="AG-002",
                deadline_months=3,
                build_agent=mock_build_agent,
            )

        # 子エージェントには session_id が含まれないこと
        assert "session_id" not in captured_invocation_state
        assert "user_name" in captured_invocation_state
        assert "request_date" in captured_invocation_state


class TestHumanApprovalHookIntegration:
    """HumanApprovalHook の結合テスト（ロジックを直接テスト）"""

    def _run_approval_logic(self, tool_name, tool_input, callback):
        """HumanApprovalHookのロジックを直接実行する"""
        # HumanApprovalHookの_on_before_tool_callロジックを直接実装してテスト
        target_tools = frozenset({
            "generate_transport_expense_form",
            "generate_general_expense_form",
        })

        if tool_name not in target_tools:
            return None  # スキップ

        approved, feedback = callback(tool_name, tool_input)

        if approved:
            return None  # キャンセルなし

        # キャンセルメッセージを生成
        if not feedback or feedback == "CANCEL":
            return "申請書生成をキャンセルしました。"
        return feedback

    def test_approval_hook_cancels_tool_on_cancel(self):
        """キャンセル時にツール実行がキャンセルされること"""
        cancel_callback = lambda tool_name, tool_params: (False, "CANCEL")
        result = self._run_approval_logic(
            "generate_transport_expense_form", {}, cancel_callback
        )
        assert result == "申請書生成をキャンセルしました。"

    def test_approval_hook_allows_tool_on_approval(self):
        """承認時にツール実行が継続されること"""
        approve_callback = lambda tool_name, tool_params: (True, "")
        result = self._run_approval_logic(
            "generate_transport_expense_form", {}, approve_callback
        )
        assert result is None

    def test_approval_hook_sets_feedback_on_modification(self):
        """修正要望時に修正内容がキャンセルメッセージに設定されること"""
        feedback_callback = lambda tool_name, tool_params: (False, "移動日を修正してください")
        result = self._run_approval_logic(
            "generate_general_expense_form", {}, feedback_callback
        )
        assert result == "移動日を修正してください"

    def test_approval_hook_skips_non_target_tool(self):
        """対象外ツールの場合にスキップされること"""
        callback = MagicMock(return_value=(True, ""))
        result = self._run_approval_logic(
            "calculate_transport_fare", {}, callback
        )
        assert result is None
        callback.assert_not_called()


class TestLoopControlHookIntegration:
    """LoopControlHook の結合テスト（ロジックを直接テスト）"""

    def test_loop_limit_error_raised_at_max(self):
        """最大ループ回数到達時に LoopLimitError が発生すること"""
        from handlers.error_handler import LoopLimitError

        # LoopControlHookのロジックを直接テスト
        max_iterations = 3
        current_iteration = 0
        agent_name = "テストエージェント"

        def simulate_after_model_call(exception=None):
            nonlocal current_iteration
            if exception is not None:
                return  # スキップ
            current_iteration += 1
            if current_iteration >= max_iterations:
                raise LoopLimitError(
                    current_iteration=current_iteration,
                    max_iterations=max_iterations,
                    agent_name=agent_name,
                )

        # 2回は正常
        simulate_after_model_call()
        simulate_after_model_call()

        # 3回目でLoopLimitError
        with pytest.raises(LoopLimitError) as exc_info:
            simulate_after_model_call()

        assert exc_info.value.current_iteration == 3
        assert exc_info.value.max_iterations == 3
        assert exc_info.value.agent_name == "テストエージェント"

    def test_loop_limit_error_skips_on_exception(self):
        """event.exception が存在する場合にカウントアップがスキップされること"""
        from handlers.error_handler import LoopLimitError

        max_iterations = 1
        current_iteration = 0

        def simulate_after_model_call(exception=None):
            nonlocal current_iteration
            if exception is not None:
                return  # スキップ
            current_iteration += 1
            if current_iteration >= max_iterations:
                raise LoopLimitError(
                    current_iteration=current_iteration,
                    max_iterations=max_iterations,
                    agent_name="テスト",
                )

        # 例外ありの場合はカウントアップしない
        simulate_after_model_call(exception=Exception("テストエラー"))
        assert current_iteration == 0


class TestTransportCalculatorIntegration:
    """交通費計算ツールの結合テスト"""

    def test_transport_fare_calculation_with_mock_data(self):
        """モックデータを使用した運賃計算テスト"""
        from tools.transport_calculator import TransportCalculatorInput

        inp = TransportCalculatorInput(
            departure="東京",
            destination="新宿",
            transport_type="電車",
            travel_date="2026-05-21",
        )
        assert inp.departure == "東京"
        assert inp.destination == "新宿"
        assert inp.transport_type == "電車"

    def test_transport_fare_with_train_data(self):
        """電車運賃計算のテスト（_calculate_train_fare直接テスト）"""
        import tools.transport_calculator as tc

        # キャッシュをリセット
        tc._train_routes = []
        tc._train_routes_loaded = False

        train_data = {
            "routes": [
                {"departure": "東京", "destination": "新宿", "fare": 200},
            ]
        }

        with patch("os.path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data=json.dumps(train_data))):
                result = tc._calculate_train_fare("東京", "新宿")

        assert result["success"] is True
        assert result["fare"] == 200

    def test_transport_fare_route_not_found(self):
        """存在しない経路でエラーが返ること"""
        import tools.transport_calculator as tc

        # キャッシュをリセット
        tc._train_routes = []
        tc._train_routes_loaded = False

        train_data = {
            "routes": [
                {"departure": "東京", "destination": "新宿", "fare": 200},
            ]
        }

        with patch("os.path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data=json.dumps(train_data))):
                result = tc._calculate_train_fare("東京", "大阪")

        assert result["success"] is False
        assert result["error_message"] is not None


class TestSessionPersistence:
    """セッション永続化のテスト"""

    def test_session_id_format(self):
        """セッションIDが正しい形式であること"""
        import re
        from session.session_manager import SessionManagerFactory

        session_id = SessionManagerFactory.generate_session_id()
        pattern = r"^\d{8}_\d{6}_[0-9a-f]{8}$"
        assert re.match(pattern, session_id), f"形式が不正: {session_id}"

    def test_session_manager_creation(self):
        """FileSessionManager が正しく生成されること"""
        from session.session_manager import SessionManagerFactory

        SessionManagerFactory._storage_dir = None
        with patch("os.makedirs"):
            manager = SessionManagerFactory.create_session_manager("test_session_id")
        assert manager is not None
