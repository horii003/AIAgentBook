"""general_expense_agent の単体テスト"""
import sys
from unittest.mock import MagicMock, patch

import pytest

# strands モジュールをモックとして登録（既存のモックを再利用）
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

# モジュールをリロード
for mod in list(sys.modules.keys()):
    if mod.startswith(("agents.general", "agents.base", "tools.", "handlers.", "session.", "config.", "models.", "prompt.", "knowledge.")):
        del sys.modules[mod]

from agents.general_expense_agent import (
    _build_general_expense_agent,
    general_expense_agent,
)
from handlers.error_handler import LoopLimitError


class TestBuildGeneralExpenseAgent:
    """_build_general_expense_agent のテスト"""

    def test_returns_agent_instance(self):
        """Agent インスタンスを返すこと"""
        with patch("os.makedirs"):
            result = _build_general_expense_agent(
                session_id="test_session",
                applicant_name="山田太郎",
                application_date="2026-05-21",
                deadline="2026-02-21",
            )
        assert result is not None


class TestGeneralExpenseAgentTool:
    """general_expense_agent ツール関数のテスト"""

    def _make_tool_context(self):
        ctx = MagicMock()
        ctx.invocation_state = {
            "user_name": "山田太郎",
            "request_date": "2026-05-21",
            "session_id": "test_session",
        }
        return ctx

    def test_returns_string(self):
        """文字列を返すこと"""
        mock_agent = MagicMock()
        mock_agent.return_value = "申請書を生成しました。"
        with patch("agents.general_expense_agent._build_general_expense_agent", return_value=mock_agent):
            with patch("os.makedirs"):
                result = general_expense_agent(
                    query="経費を申請したい",
                    tool_context=self._make_tool_context(),
                )
        assert isinstance(result, str)

    def test_loop_limit_error_returns_message(self):
        """LoopLimitError 発生時にエラーメッセージを返すこと"""
        mock_agent = MagicMock()
        mock_agent.side_effect = LoopLimitError(10, 10, "経費精算申請エージェント")
        with patch("agents.general_expense_agent._build_general_expense_agent", return_value=mock_agent):
            with patch("os.makedirs"):
                result = general_expense_agent(
                    query="経費を申請したい",
                    tool_context=self._make_tool_context(),
                )
        assert isinstance(result, str)
        assert len(result) > 0
