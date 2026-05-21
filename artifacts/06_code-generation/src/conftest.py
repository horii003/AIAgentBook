"""テスト共通設定。

全テストで共通のモック設定を行う。
strands等の外部ライブラリをモックとして登録する。
"""
import sys
from unittest.mock import MagicMock


def _setup_mocks():
    """外部ライブラリのモックを設定する。"""
    # strands モジュールをモックとして登録
    if "strands" not in sys.modules:
        mock_strands = MagicMock()
        sys.modules["strands"] = mock_strands
        sys.modules["strands.models"] = mock_strands.models

    mock_strands = sys.modules["strands"]
    mock_strands.Agent = MagicMock
    mock_strands.ModelRetryStrategy = MagicMock
    mock_strands.ToolContext = MagicMock
    # @tool デコレータをモック（関数をそのまま返す）
    mock_strands.tool = lambda *args, **kwargs: (lambda f: f) if args and callable(args[0]) else (lambda f: f)

    # strands.agent.conversation_manager をモック
    if "strands.agent" not in sys.modules:
        sys.modules["strands.agent"] = MagicMock()
    if "strands.agent.conversation_manager" not in sys.modules:
        mock_conv = MagicMock()
        mock_conv.SlidingWindowConversationManager = MagicMock
        sys.modules["strands.agent.conversation_manager"] = mock_conv
    else:
        if not hasattr(sys.modules["strands.agent.conversation_manager"], "SlidingWindowConversationManager"):
            sys.modules["strands.agent.conversation_manager"].SlidingWindowConversationManager = MagicMock

    # strands.hooks をモック（HookProviderを実際のクラスとして定義）
    if "strands.hooks" not in sys.modules:
        mock_hooks = MagicMock()
        mock_hooks.HookProvider = type("HookProvider", (), {})
        mock_hooks.HookRegistry = MagicMock
        for event in ["BeforeToolCallEvent", "BeforeInvocationEvent", "AfterInvocationEvent",
                      "BeforeModelCallEvent", "AfterModelCallEvent", "AfterToolCallEvent"]:
            setattr(mock_hooks, event, MagicMock)
        sys.modules["strands.hooks"] = mock_hooks
    else:
        hooks_mod = sys.modules["strands.hooks"]
        if not hasattr(hooks_mod, "HookProvider") or not isinstance(hooks_mod.HookProvider, type):
            hooks_mod.HookProvider = type("HookProvider", (), {})
        for event in ["BeforeToolCallEvent", "BeforeInvocationEvent", "AfterInvocationEvent",
                      "BeforeModelCallEvent", "AfterModelCallEvent", "AfterToolCallEvent"]:
            if not hasattr(hooks_mod, event):
                setattr(hooks_mod, event, MagicMock)

    # strands.session.file_session_manager をモック
    if "strands.session" not in sys.modules:
        sys.modules["strands.session"] = MagicMock()
    if "strands.session.file_session_manager" not in sys.modules:
        mock_fsm = MagicMock()
        sys.modules["strands.session.file_session_manager"] = mock_fsm

    # openpyxl をモック
    if "openpyxl" not in sys.modules:
        sys.modules["openpyxl"] = MagicMock()


# テスト開始前にモックを設定
_setup_mocks()
