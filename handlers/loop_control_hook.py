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
from handlers.error_handler import ErrorHandler, LoopLimitError


class LoopControlHook(HookProvider):
    """
    ReActループの最大回数を制御するフック
    
    このフックは以下の機能を提供します：
    1. BeforeInvocationEventでループカウントを初期化
    2. AfterModelCallEventでループカウントをインクリメント
    3. 最大回数に達した場合はRuntimeErrorを発生させる
    4. エージェントのフロー（状態）を表示
    
    Note:
        全フックイベントはStrandsの_run_loop()内（BeforeInvocationEvent～AfterInvocationEventの間）
        でのみ発火され、かつ_invocation_lockにより同一インスタンスへの並行呼び出しもブロックされるため、
        invocation外での発火を防ぐガードは不要です。
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
        self._error_handler = ErrorHandler()  # ErrorHandlerを使用
    
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
        self._error_handler.log_info(f"[{self.agent_name}] BeforeInvocationEvent: エージェント呼び出し開始")
        self._error_handler.log_info(f"[{self.agent_name}] 最大ループ回数: {self.max_iterations}")
    
    def on_before_model_call(self, event: BeforeModelCallEvent) -> None:
        """
        モデル呼び出し前の処理
        
        Args:
            event: BeforeModelCallEvent
        """
        self._error_handler.log_info(f"[{self.agent_name}] BeforeModelCallEvent: モデル呼び出し #{self.current_iteration + 1}")
    
    def on_after_model_call(self, event: AfterModelCallEvent) -> None:
        """
        モデル呼び出し後の処理
        
        Args:
            event: AfterModelCallEvent
        """
        # 例外が発生している場合はカウントしない（retry処理を避ける）
        if event.exception:
            return
        
        # ループカウントをインクリメント
        self.current_iteration += 1
        
        self._error_handler.log_info(
            f"[{self.agent_name}] AfterModelCallEvent: モデル呼び出し完了 ({self.current_iteration}/{self.max_iterations})"
        )
        
        # 最大回数チェック
        if self.current_iteration >= self.max_iterations:
            # 警告ログを出力
            self._error_handler.log_warning(
                f"[{self.agent_name}] ループ制限到達: {self.current_iteration}/{self.max_iterations}"
            )
            
            # LoopLimitErrorを発生
            raise LoopLimitError(
                current_iteration=self.current_iteration,
                max_iterations=self.max_iterations,
                agent_name=self.agent_name
            )
    
    def on_before_tool_call(self, event: BeforeToolCallEvent) -> None:
        """
        ツール呼び出し前の処理
        
        Args:
            event: BeforeToolCallEvent
        """
        tool_name = event.tool_use.get("name", "unknown")
        self._error_handler.log_info(f"[{self.agent_name}] BeforeToolCallEvent: ツール呼び出し - {tool_name}")
    
    def on_after_tool_call(self, event: AfterToolCallEvent) -> None:
        """
        ツール呼び出し後の処理
        
        Args:
            event: AfterToolCallEvent
        """
        tool_name = event.tool_use.get("name", "unknown")
        self._error_handler.log_info(f"[{self.agent_name}] AfterToolCallEvent: ツール呼び出し完了 - {tool_name}")
    
    def on_after_invocation(self, event: AfterInvocationEvent) -> None:
        """
        エージェント呼び出し終了時の処理
        
        Args:
            event: AfterInvocationEvent
        """
        self._error_handler.log_info(
            f"[{self.agent_name}] AfterInvocationEvent: エージェント呼び出し終了（合計ループ回数: {self.current_iteration}）"
        )
