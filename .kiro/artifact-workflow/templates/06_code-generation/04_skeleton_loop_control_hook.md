# スケルトン: ReActループ制御フック (handlers/loop_control_hook.py)

## 概要

エージェントのReActループの最大回数を制御し、ループの状態を表示するフック。
全エージェントで共通利用する。

## ファイル配置

`handlers/loop_control_hook.py`

## スケルトンコード

```python
"""
ReActループ制御フック

エージェントのReActループの最大回数を制御し、
ループの状態を表示するフック。
"""
import logging
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
from handlers.error_handler import LoopLimitError

_logger = logging.getLogger(__name__)


class LoopControlHook(HookProvider):
    """
    ReActループの最大回数を制御するフック

    このフックは以下の機能を提供します：
    1. BeforeInvocationEventでループカウントを初期化
    2. AfterModelCallEventでループカウントをインクリメント
    3. 最大回数に達した場合はLoopLimitErrorを発生させる
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

    def register_hooks(self, registry: HookRegistry, **kwargs: Any) -> None:
        """フックの登録"""
        # TODO: 詳細設計書に従い実装
        # - 6つのイベントにコールバックを登録
        pass

    def on_before_invocation(self, event: BeforeInvocationEvent) -> None:
        """
        エージェント呼び出し開始時の処理

        Args:
            event: BeforeInvocationEvent
        """
        # TODO: 詳細設計書に従い実装
        # - ループカウントの初期化
        # - 呼び出し開始のログ出力
        pass

    def on_before_model_call(self, event: BeforeModelCallEvent) -> None:
        """
        モデル呼び出し前の処理

        Args:
            event: BeforeModelCallEvent
        """
        # TODO: 詳細設計書に従い実装
        # - 現在のループ回数をログ出力
        pass

    def on_after_model_call(self, event: AfterModelCallEvent) -> None:
        """
        モデル呼び出し後の処理

        Args:
            event: AfterModelCallEvent
        """
        # TODO: 詳細設計書に従い実装
        # - 例外発生時のスキップ判定（event.exceptionが存在する場合はreturn）
        #   ※ Strands Agents SDKはモデル呼び出しの成功・失敗両方でAfterModelCallEventを発火するため必須
        # - ループカウントのインクリメント
        # - ログ出力
        # - 最大回数チェックとLoopLimitError発生
        pass

    def _get_tool_name(self, event) -> str:
        """ツール名を安全に取得するヘルパー（R9.8.6参照）"""
        # TODO: event.tool_use が None の場合は "unknown" を返す
        return event.tool_use["name"] if event.tool_use else "unknown"

    def on_before_tool_call(self, event: BeforeToolCallEvent) -> None:
        """
        ツール呼び出し前の処理

        Args:
            event: BeforeToolCallEvent
        """
        # TODO: 詳細設計書に従い実装
        # - _get_tool_name(event) でツール名を取得してログ出力
        pass

    def on_after_tool_call(self, event: AfterToolCallEvent) -> None:
        """
        ツール呼び出し後の処理

        Args:
            event: AfterToolCallEvent
        """
        # TODO: 詳細設計書に従い実装
        # - _get_tool_name(event) でツール名を取得して完了ログ出力
        pass

    def on_after_invocation(self, event: AfterInvocationEvent) -> None:
        """
        エージェント呼び出し終了時の処理

        Args:
            event: AfterInvocationEvent
        """
        # TODO: 詳細設計書に従い実装
        # - 合計ループ回数のログ出力
        pass
```

## カスタマイズガイド

- このモジュールは汎用的なため、基本的にカスタマイズ不要
- `max_iterations` のデフォルト値はプロジェクト要件に応じて調整可能
- エージェントごとにインスタンス生成時に `max_iterations` と `agent_name` を指定する
