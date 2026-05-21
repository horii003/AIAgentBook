"""base_agent の単体テスト"""
import sys
from unittest.mock import MagicMock, patch

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

# strands.agent.conversation_manager をモック
mock_conv_manager = MagicMock()
sys.modules.setdefault("strands.agent", MagicMock())
sys.modules.setdefault("strands.agent.conversation_manager", mock_conv_manager)
mock_conv_manager.SlidingWindowConversationManager = MagicMock

# strands.hooks をモック（既にモック済みの場合はスキップ）
if "strands.hooks" not in sys.modules:
    mock_hooks = MagicMock()
    mock_hooks.HookProvider = type("HookProvider", (), {})
    mock_hooks.HookRegistry = MagicMock
    mock_hooks.BeforeToolCallEvent = MagicMock
    mock_hooks.BeforeInvocationEvent = MagicMock
    mock_hooks.AfterInvocationEvent = MagicMock
    mock_hooks.BeforeModelCallEvent = MagicMock
    mock_hooks.AfterModelCallEvent = MagicMock
    mock_hooks.AfterToolCallEvent = MagicMock
    sys.modules["strands.hooks"] = mock_hooks

# strands.session.file_session_manager をモック
if "strands.session.file_session_manager" not in sys.modules:
    mock_fsm = MagicMock()
    sys.modules.setdefault("strands.session", MagicMock())
    sys.modules["strands.session.file_session_manager"] = mock_fsm

# モジュールをリロード
for mod in ["agents.base_agent", "handlers.loop_control_hook", "handlers.human_approval_hook",
            "session.session_manager", "config.model_config"]:
    if mod in sys.modules:
        del sys.modules[mod]

from agents.base_agent import calculate_deadline, create_specialist_agent, invoke_specialist_agent
from handlers.error_handler import LoopLimitError


class TestCalculateDeadline:
    """calculate_deadline のテスト"""

    def test_normal_calculation(self):
        """正常な期限計算"""
        result = calculate_deadline("2026-05-21", 3)
        assert result == "2026-02-21"

    def test_parse_failure_returns_yokakunin(self):
        """パース失敗時に '要確認' を返すこと"""
        result = calculate_deadline("invalid-date", 3)
        assert result == "要確認"

    def test_different_months(self):
        """異なる月数での計算"""
        result = calculate_deadline("2026-06-01", 6)
        assert result == "2025-12-01"


class TestCreateSpecialistAgent:
    """create_specialist_agent のテスト"""

    def test_returns_agent_instance(self):
        """Agent インスタンスを返すこと"""
        with patch("os.makedirs"):
            result = create_specialist_agent(
                session_id="test_session",
                system_prompt="テストプロンプト",
                tools=[],
                agent_name="テストエージェント",
                window_size=20,
                max_iterations=10,
                max_attempts=6,
                initial_delay=4,
                max_delay=240,
            )
        assert result is not None


class TestInvokeSpecialistAgent:
    """invoke_specialist_agent のテスト"""

    def _make_tool_context(self):
        """ToolContext のモックを作成する"""
        ctx = MagicMock()
        ctx.invocation_state = {
            "user_name": "山田太郎",
            "request_date": "2026-05-21",
            "session_id": "test_session_id",
        }
        return ctx

    def test_loop_limit_error_returns_message(self):
        """LoopLimitError 発生時にエラーメッセージを返すこと"""
        mock_agent = MagicMock()
        mock_agent.side_effect = LoopLimitError(10, 10, "テストエージェント")
        mock_build = MagicMock(return_value=mock_agent)

        with patch("os.makedirs"):
            result = invoke_specialist_agent(
                query="テストクエリ",
                tool_context=self._make_tool_context(),
                agent_id="AG-002",
                deadline_months=3,
                build_agent=mock_build,
            )
        assert isinstance(result, str)
        assert len(result) > 0

    def test_exception_returns_message(self):
        """Exception 発生時にエラーメッセージを返すこと"""
        mock_agent = MagicMock()
        mock_agent.side_effect = Exception("テストエラー")
        mock_build = MagicMock(return_value=mock_agent)

        with patch("os.makedirs"):
            result = invoke_specialist_agent(
                query="テストクエリ",
                tool_context=self._make_tool_context(),
                agent_id="AG-002",
                deadline_months=3,
                build_agent=mock_build,
            )
        assert isinstance(result, str)
        assert len(result) > 0
