"""LoopControlHook の単体テスト"""
import sys
from unittest.mock import MagicMock, patch

import pytest

# strands.hooks モジュールをモックとして登録
mock_strands_hooks = MagicMock()

# HookProvider の基底クラスをモック
class MockHookProvider:
    pass

mock_strands_hooks.HookProvider = MockHookProvider
mock_strands_hooks.HookRegistry = MagicMock
mock_strands_hooks.BeforeInvocationEvent = MagicMock
mock_strands_hooks.AfterInvocationEvent = MagicMock
mock_strands_hooks.BeforeModelCallEvent = MagicMock
mock_strands_hooks.AfterModelCallEvent = MagicMock
mock_strands_hooks.BeforeToolCallEvent = MagicMock
mock_strands_hooks.AfterToolCallEvent = MagicMock

sys.modules.setdefault("strands", MagicMock())
sys.modules.setdefault("strands.hooks", mock_strands_hooks)
sys.modules.setdefault("strands.models", MagicMock())

# モジュールをリロードして確実にモックを使用させる
if "handlers.loop_control_hook" in sys.modules:
    del sys.modules["handlers.loop_control_hook"]

from handlers.error_handler import LoopLimitError
from handlers.loop_control_hook import LoopControlHook


def _make_model_call_event(exception=None):
    """AfterModelCallEvent のモックを作成する"""
    event = MagicMock()
    event.exception = exception
    return event


def _make_tool_call_event(tool_name="test_tool"):
    """BeforeToolCallEvent / AfterToolCallEvent のモックを作成する"""
    event = MagicMock()
    event.tool_use = {"name": tool_name}
    return event


class TestLoopControlHookInit:
    """LoopControlHook の初期化テスト"""

    def test_default_max_iterations(self):
        """デフォルトの最大ループ回数が10であること"""
        hook = LoopControlHook()
        assert hook._max_iterations == 10

    def test_custom_max_iterations(self):
        """カスタムの最大ループ回数が設定されること"""
        hook = LoopControlHook(max_iterations=5)
        assert hook._max_iterations == 5

    def test_initial_current_iteration(self):
        """初期ループ回数が0であること"""
        hook = LoopControlHook()
        assert hook._current_iteration == 0


class TestRegisterHooks:
    """register_hooks のテスト"""

    def test_registers_six_events(self):
        """6つのイベントが登録されること"""
        hook = LoopControlHook()
        registry = MagicMock()
        hook.register_hooks(registry)
        assert registry.add_callback.call_count == 6


class TestOnBeforeInvocation:
    """on_before_invocation のテスト"""

    def test_resets_current_iteration(self):
        """ループカウンタが0にリセットされること"""
        hook = LoopControlHook()
        hook._current_iteration = 5
        event = MagicMock()
        hook.on_before_invocation(event)
        assert hook._current_iteration == 0


class TestOnAfterModelCall:
    """on_after_model_call のテスト"""

    def test_increments_counter(self):
        """ループカウンタがインクリメントされること"""
        hook = LoopControlHook(max_iterations=10)
        event = _make_model_call_event()
        hook.on_after_model_call(event)
        assert hook._current_iteration == 1

    def test_raises_loop_limit_error_at_max(self):
        """最大回数到達時にLoopLimitErrorが発生すること"""
        hook = LoopControlHook(max_iterations=3, agent_name="テストエージェント")
        event = _make_model_call_event()
        # 2回は正常
        hook.on_after_model_call(event)
        hook.on_after_model_call(event)
        # 3回目でLoopLimitError
        with pytest.raises(LoopLimitError) as exc_info:
            hook.on_after_model_call(event)
        assert exc_info.value.current_iteration == 3
        assert exc_info.value.max_iterations == 3
        assert exc_info.value.agent_name == "テストエージェント"

    def test_skips_increment_when_exception_exists(self):
        """event.exception が存在する場合にカウントアップがスキップされること"""
        hook = LoopControlHook(max_iterations=10)
        event = _make_model_call_event(exception=Exception("テストエラー"))
        hook.on_after_model_call(event)
        assert hook._current_iteration == 0

    def test_raises_at_max_iterations_1(self):
        """max_iterations=1 の場合に1回目でLoopLimitErrorが発生すること"""
        hook = LoopControlHook(max_iterations=1)
        event = _make_model_call_event()
        with pytest.raises(LoopLimitError):
            hook.on_after_model_call(event)


class TestGetToolName:
    """_get_tool_name のテスト"""

    def test_returns_tool_name(self):
        """tool_use が存在する場合にツール名を返すこと"""
        hook = LoopControlHook()
        event = _make_tool_call_event("my_tool")
        assert hook._get_tool_name(event) == "my_tool"

    def test_returns_unknown_when_tool_use_is_none(self):
        """tool_use が None の場合に 'unknown' を返すこと"""
        hook = LoopControlHook()
        event = MagicMock()
        event.tool_use = None
        assert hook._get_tool_name(event) == "unknown"
