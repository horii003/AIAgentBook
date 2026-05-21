"""ReActループ制御フックの単体テスト"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import pytest
from unittest.mock import MagicMock
from handlers.loop_control_hook import LoopControlHook
from handlers.error_handler import LoopLimitError


def _make_model_event(exception=None):
    """AfterModelCallEvent のモックを作成する。"""
    event = MagicMock()
    event.exception = exception
    return event


def _make_tool_event(tool_name=None):
    """BeforeToolCallEvent / AfterToolCallEvent のモックを作成する。"""
    event = MagicMock()
    if tool_name is None:
        event.tool_use = None
    else:
        event.tool_use = {"name": tool_name}
    return event


class TestLoopControlHook:
    """LoopControlHook のテスト"""

    def test_on_before_invocation_resets_counter(self):
        """on_before_invocation でカウンターが 0 にリセットされること"""
        hook = LoopControlHook(max_iterations=10, agent_name="テスト")
        hook.current_iteration = 5
        hook.on_before_invocation(MagicMock())
        assert hook.current_iteration == 0

    def test_on_after_model_call_increments_counter(self):
        """on_after_model_call でカウンターがインクリメントされること"""
        hook = LoopControlHook(max_iterations=10, agent_name="テスト")
        event = _make_model_event(exception=None)
        hook.on_after_model_call(event)
        assert hook.current_iteration == 1

    def test_on_after_model_call_skips_on_exception(self):
        """on_after_model_call で event.exception がある場合はスキップされること"""
        hook = LoopControlHook(max_iterations=10, agent_name="テスト")
        event = _make_model_event(exception=RuntimeError("error"))
        hook.on_after_model_call(event)
        assert hook.current_iteration == 0

    def test_on_after_model_call_raises_loop_limit_error_at_max(self):
        """上限到達時に LoopLimitError が raise されること"""
        hook = LoopControlHook(max_iterations=3, agent_name="テストエージェント")
        event = _make_model_event(exception=None)
        hook.on_after_model_call(event)  # 1
        hook.on_after_model_call(event)  # 2
        with pytest.raises(LoopLimitError) as exc_info:
            hook.on_after_model_call(event)  # 3 → 上限到達
        assert exc_info.value.agent_name == "テストエージェント"
        assert exc_info.value.max_iterations == 3

    def test_get_tool_name_returns_unknown_when_tool_use_is_none(self):
        """_get_tool_name が tool_use=None の場合に "unknown" を返すこと"""
        hook = LoopControlHook()
        event = _make_tool_event(tool_name=None)
        assert hook._get_tool_name(event) == "unknown"

    def test_get_tool_name_returns_tool_name(self):
        """_get_tool_name がツール名を返すこと"""
        hook = LoopControlHook()
        event = _make_tool_event(tool_name="calculate_transport_fare")
        assert hook._get_tool_name(event) == "calculate_transport_fare"
