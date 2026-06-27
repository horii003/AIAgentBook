"""LoopControlHookの単体テスト"""
from unittest.mock import MagicMock, patch
import pytest

from handlers.error_handler import LoopLimitError
from handlers.loop_control_hook import LoopControlHook


class TestLoopControlHook:
    """LoopControlHookのテスト"""

    def test_default_max_iterations(self):
        hook = LoopControlHook()
        assert hook._max_iterations == 10

    def test_custom_max_iterations(self):
        hook = LoopControlHook(max_iterations=5)
        assert hook._max_iterations == 5

    def test_before_invocation_resets_count(self):
        hook = LoopControlHook()
        hook._loop_count = 5
        event = MagicMock()
        hook._handle_before_invocation(event)
        assert hook._loop_count == 0

    def test_after_model_call_increments(self):
        hook = LoopControlHook(max_iterations=10)
        event = MagicMock()
        event.exception = None
        hook._handle_after_model_call(event)
        assert hook._loop_count == 1

    def test_after_model_call_skips_on_exception(self):
        hook = LoopControlHook(max_iterations=10)
        event = MagicMock()
        event.exception = Exception("test")
        hook._handle_after_model_call(event)
        assert hook._loop_count == 0

    def test_raises_loop_limit_error_at_max(self):
        hook = LoopControlHook(max_iterations=3, agent_name="TestAgent")
        event = MagicMock()
        event.exception = None

        # 2回は正常
        hook._handle_after_model_call(event)
        hook._handle_after_model_call(event)

        # 3回目でLoopLimitError
        with pytest.raises(LoopLimitError) as exc_info:
            hook._handle_after_model_call(event)

        assert exc_info.value.current_iteration == 3
        assert exc_info.value.max_iterations == 3
        assert exc_info.value.agent_name == "TestAgent"

    def test_after_invocation_does_not_reset(self):
        hook = LoopControlHook()
        hook._loop_count = 5
        event = MagicMock()
        hook._handle_after_invocation(event)
        assert hook._loop_count == 5  # リセットされない

    def test_register_hooks_calls_add_callback_six_times(self):
        hook = LoopControlHook()
        registry = MagicMock()
        hook.register_hooks(registry)
        assert registry.add_callback.call_count == 6

    def test_get_tool_name_with_tool_use(self):
        hook = LoopControlHook()
        event = MagicMock()
        event.tool_use = {"name": "my_tool"}
        assert hook._get_tool_name(event) == "my_tool"

    def test_get_tool_name_without_tool_use(self):
        hook = LoopControlHook()
        event = MagicMock()
        event.tool_use = None
        assert hook._get_tool_name(event) == "unknown"
