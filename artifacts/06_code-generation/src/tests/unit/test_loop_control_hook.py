"""LoopControlHookの単体テスト"""
import pytest
from unittest.mock import MagicMock
from handlers.loop_control_hook import LoopControlHook
from handlers.error_handler import LoopLimitError


def make_after_model_event(exception=None):
    """AfterModelCallEventのモックを作成する"""
    event = MagicMock()
    event.exception = exception
    return event


def make_tool_event(tool_name="test_tool"):
    """BeforeToolCallEvent/AfterToolCallEventのモックを作成する"""
    event = MagicMock()
    event.tool_use = {"name": tool_name}
    return event


class TestLoopControlHook:
    def test_no_error_below_limit(self):
        """TC-UNIT-043: ループ回数が上限未満でエラーが発生しないこと"""
        hook = LoopControlHook(max_iterations=10, agent_name="テスト")
        # BeforeInvocationでリセット
        hook._handle_before_invocation(MagicMock())
        # 9回AfterModelCallを発火
        for _ in range(9):
            hook._handle_after_model_call(make_after_model_event())
        assert hook._iteration_count == 9

    def test_raises_at_limit(self):
        """TC-UNIT-044: ループ回数が上限に達した場合にLoopLimitErrorが発生すること"""
        hook = LoopControlHook(max_iterations=10, agent_name="テスト")
        hook._handle_before_invocation(MagicMock())
        with pytest.raises(LoopLimitError) as exc_info:
            for _ in range(10):
                hook._handle_after_model_call(make_after_model_event())
        assert exc_info.value.current_iteration == 10
        assert exc_info.value.max_iterations == 10

    def test_reset_on_before_invocation(self):
        """TC-UNIT-045: BeforeInvocationEventでカウンタが0にリセットされること"""
        hook = LoopControlHook(max_iterations=10)
        hook._iteration_count = 5
        hook._handle_before_invocation(MagicMock())
        assert hook._iteration_count == 0

    def test_skip_on_exception(self):
        """AfterModelCallEventでevent.exceptionが存在する場合にカウントアップがスキップされること"""
        hook = LoopControlHook(max_iterations=10)
        hook._handle_before_invocation(MagicMock())
        hook._handle_after_model_call(make_after_model_event(exception=Exception("test")))
        assert hook._iteration_count == 0

    def test_no_reset_on_after_invocation(self):
        """AfterInvocationEventでカウンタがリセットされないこと"""
        hook = LoopControlHook(max_iterations=10)
        hook._handle_before_invocation(MagicMock())
        for _ in range(3):
            hook._handle_after_model_call(make_after_model_event())
        hook._handle_after_invocation(MagicMock())
        assert hook._iteration_count == 3

    def test_raises_at_limit_1(self):
        """max_iterations=1の場合に1回目でLoopLimitErrorが発生すること"""
        hook = LoopControlHook(max_iterations=1)
        hook._handle_before_invocation(MagicMock())
        with pytest.raises(LoopLimitError):
            hook._handle_after_model_call(make_after_model_event())

    def test_get_tool_name_with_none(self):
        """tool_useがNoneの場合に'unknown'を返すこと"""
        hook = LoopControlHook()
        event = MagicMock()
        event.tool_use = None
        assert hook._get_tool_name(event) == "unknown"
