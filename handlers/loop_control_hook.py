"""
ReActループ制御フック

エージェントのReActループの最大回数を制御し、
ループの状態を表示するフック。
"""

from typing import Any
from strands.hooks import (
    HookProvider, 
    HookRegistry, 
    BeforeInvocationEvent,
    AfterModelCallEvent,
    BeforeModelCallEvent,
    AfterInvocationEvent,
    BeforeToolCallEvent,
    AfterToolCallEvent
)
import logging

logger = logging.getLogger(__name__)


class LoopControlHook(HookProvider):
    """
    ReActループの最大回数を制御するフック
    
    このフックは以下の機能を提供します：
    1. BeforeInvocationEventでループカウントを初期化
    2. AfterModelCallEventでループカウントをインクリメント
    3. 最大回数に達した場合はRuntimeErrorを発生させる
    4. エージェントのフロー（状態）を表示
    """
    
    def __init__(self, max_iterations: int = 10, agent_name: str = "Agent"):
        """
        初期化
        
        Args:
            max_iterations: 最大ループ回数（デフォルト: 10）
            agent_name: エージェント名（ログ表示用）
        """
        self.max_iterations = max_iterations
        self.agent_name = agent_name
        self.current_iteration = 0
        self._invocation_active = False
    
    def register_hooks(self, registry: HookRegistry, **kwargs: Any) -> None:
        """フックの登録"""
        registry.add_callback(BeforeInvocationEvent, self.on_before_invocation)
        registry.add_callback(BeforeModelCallEvent, self.on_before_model_call)
        registry.add_callback(AfterModelCallEvent, self.on_after_model_call)
        registry.add_callback(BeforeToolCallEvent, self.on_before_tool_call)
        registry.add_callback(AfterToolCallEvent, self.on_after_tool_call)
        registry.add_callback(AfterInvocationEvent, self.on_after_invocation)
    
    def on_before_invocation(self, event: BeforeInvocationEvent) -> None:
        """
        エージェント呼び出し開始時の処理
        
        Args:
            event: BeforeInvocationEvent
        """
        self.current_iteration = 0
        self._invocation_active = True
        logger.info(f"[{self.agent_name}] BeforeInvocationEvent: エージェント呼び出し開始")
        logger.info(f"[{self.agent_name}] 最大ループ回数: {self.max_iterations}")
    
    def on_before_model_call(self, event: BeforeModelCallEvent) -> None:
        """
        モデル呼び出し前の処理
        
        Args:
            event: BeforeModelCallEvent
        """
        if not self._invocation_active:
            return
        
        logger.info(f"[{self.agent_name}] BeforeModelCallEvent: モデル呼び出し #{self.current_iteration + 1}")
    
    def on_after_model_call(self, event: AfterModelCallEvent) -> None:
        """
        モデル呼び出し後の処理
        
        Args:
            event: AfterModelCallEvent
        """
        if not self._invocation_active:
            return
        
        # 例外が発生している場合はカウントしない（retry処理を避ける）
        if event.exception:
            return
        
        # ループカウントをインクリメント
        self.current_iteration += 1
        
        logger.info(f"[{self.agent_name}] AfterModelCallEvent: モデル呼び出し完了 ({self.current_iteration}/{self.max_iterations})")
        
        # 最大回数チェック
        if self.current_iteration >= self.max_iterations:
            error_message = (
                f"エージェントループの制限に到達しました（{self.max_iterations}回）。\n"
                f"タスクが複雑すぎる可能性があります。\n"
                f"以下のいずれかをお試しください：\n"
                f"1. タスクをより小さな単位に分割する\n"
                f"2. より具体的な指示を提供する\n"
                f"3. 不要な情報を削除する"
            )
            # エラー発生をログに記録
            logger.warning(f"[{self.agent_name}] ループ制限到達: {self.current_iteration}/{self.max_iterations}")
            raise RuntimeError(error_message)
    
    def on_before_tool_call(self, event: BeforeToolCallEvent) -> None:
        """
        ツール呼び出し前の処理
        
        Args:
            event: BeforeToolCallEvent
        """
        if not self._invocation_active:
            return
        
        tool_name = event.tool_use.get("name", "unknown")
        logger.info(f"[{self.agent_name}] BeforeToolCallEvent: ツール呼び出し - {tool_name}")
    
    def on_after_tool_call(self, event: AfterToolCallEvent) -> None:
        """
        ツール呼び出し後の処理
        
        Args:
            event: AfterToolCallEvent
        """
        if not self._invocation_active:
            return
        
        tool_name = event.tool_use.get("name", "unknown")
        logger.info(f"[{self.agent_name}] AfterToolCallEvent: ツール呼び出し完了 - {tool_name}")
    
    def on_after_invocation(self, event: AfterInvocationEvent) -> None:
        """
        エージェント呼び出し終了時の処理
        
        Args:
            event: AfterInvocationEvent
        """
        if not self._invocation_active:
            return
        
        self._invocation_active = False
        logger.info(f"[{self.agent_name}] AfterInvocationEvent: エージェント呼び出し終了（合計ループ回数: {self.current_iteration}）")
