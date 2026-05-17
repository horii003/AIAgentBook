"""ループ制御フックの単体テスト"""

from unittest.mock import MagicMock

import pytest

from handlers.error_handler import LoopLimitError
from handlers.loop_control_hook import LoopControlHook


def _make_after_model_call_event(exception=None):
    event = MagicMock()
    event.exception = exception
    return event


def _make_before_invocation_event():
    return MagicMock()


def _make_before_tool_call_event(tool_name="test_tool"):
    event = MagicMock()
    event.tool_use = {"name": tool_name, "input": {}, "toolUseId": "id1"}
    return event


def _make_after_tool_call_event(tool_name="test_tool"):
    event = MagicMock()
    event.tool_use = {"name": tool_name, "input": {}, "toolUseId": "id1"}
    return event


class TestLoopControlHook:
    """LoopControlHook のテスト"""

    def test_normal_iterations(self):
        """9回のモデル呼び出しで正常動作すること"""
        hook = LoopControlHook(max_iterations=10, agent_name="test")
        hook._handle_before_invocation(_make_before_invocation_event())
        for _ in range(9):
            hook._handle_after_model_call(_make_after_model_call_event())
        # 9回目まで正常
        assert hook._iteration_count == 9

    def test_loop_limit_error_at_max(self):
        """10回目でLoopLimitErrorが発生すること"""
        hook = LoopControlHook(max_iterations=10, agent_name="test")
        hook._handle_before_invocation(_make_before_invocation_event())
        for _ in range(9):
            hook._handle_after_model_call(_make_after_model_call_event())
        with pytest.raises(LoopLimitError) as exc_info:
            hook._handle_after_model_call(_make_after_model_call_event())
        assert exc_info.value.current_iteration == 10
        assert exc_info.value.max_iterations == 10
        assert exc_info.value.agent_name == "test"

    def test_reset_on_before_invocation(self):
        """BeforeInvocationでカウントがリセットされること"""
        hook = LoopControlHook(max_iterations=10, agent_name="test")
        hook._iteration_count = 5
        hook._handle_before_invocation(_make_before_invocation_event())
        assert hook._iteration_count == 0

    def test_skip_on_exception(self):
        """event.exceptionが設定されている場合にスキップすること"""
        hook = LoopControlHook(max_iterations=10, agent_name="test")
        hook._handle_before_invocation(_make_before_invocation_event())
        hook._handle_after_model_call(
            _make_after_model_call_event(exception=Exception("err"))
        )
        assert hook._iteration_count == 0

    def test_max_iterations_one(self):
        """max_iterations=1の場合、1回で発生すること"""
        hook = LoopControlHook(max_iterations=1, agent_name="test")
        hook._handle_before_invocation(_make_before_invocation_event())
        with pytest.raises(LoopLimitError):
            hook._handle_after_model_call(_make_after_model_call_event())

    def test_before_tool_call_logs(self):
        """BeforeToolCallEventでツール名を取得できること"""
        hook = LoopControlHook(max_iterations=10, agent_name="test")
        event = _make_before_tool_call_event("my_tool")
        hook._handle_before_tool_call(event)  # ログ出力のみ、例外なし

    def test_after_tool_call_logs(self):
        """AfterToolCallEventでツール名を取得できること"""
        hook = LoopControlHook(max_iterations=10, agent_name="test")
        event = _make_after_tool_call_event("my_tool")
        hook._handle_after_tool_call(event)  # ログ出力のみ、例外なし

    def test_get_tool_name_none(self):
        """tool_useがNoneの場合にunknownを返すこと"""
        hook = LoopControlHook(max_iterations=10, agent_name="test")
        event = MagicMock()
        event.tool_use = None
        assert hook._get_tool_name(event) == "unknown"
