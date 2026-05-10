# スケルトン: メインエントリーポイント (main.py)

## 概要

アプリケーションのエントリーポイント。
環境変数の読み込み、ログ設定、オーケストレーターエージェントの起動を行う。

## ファイル配置

`main.py`（プロジェクトルート）

## スケルトンコード

```python
"""マルチエージェントアプリケーション - メインエントリーポイント"""
import sys
import os
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
from agents.orchestrator_agent import OrchestratorAgent
from handlers.error_handler import ErrorHandler


# .envファイルを読み込み
load_dotenv()

# TODO: 詳細設計書に従い実装
# - LOG_LEVEL環境変数の取得（デフォルト: INFO）
#   log_level = getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO)
#
# - ログディレクトリの作成
#   os.makedirs("logs", exist_ok=True)
#
# - ログフォーマッターの作成
#   _fmt = "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
#   _formatter = logging.Formatter(_fmt)
#
# - app.log ハンドラー（INFO以上、RotatingFileHandler: 10MB × 5世代）
#   _app_handler = RotatingFileHandler(
#       "logs/app.log", maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
#   )
#   _app_handler.setLevel(logging.INFO)
#   _app_handler.setFormatter(_formatter)
#
# - error.log ハンドラー（ERROR以上、RotatingFileHandler: 10MB × 5世代）
#   _error_handler_file = RotatingFileHandler(
#       "logs/error.log", maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
#   )
#   _error_handler_file.setLevel(logging.ERROR)
#   _error_handler_file.setFormatter(_formatter)
#
# - コンソールハンドラー（INFO以上）
#   _console_handler = logging.StreamHandler()
#   _console_handler.setLevel(logging.INFO)
#   _console_handler.setFormatter(_formatter)
#
# - logging.basicConfigの設定（3ハンドラー構成）
#   logging.basicConfig(
#       level=log_level,
#       handlers=[_console_handler, _app_handler, _error_handler_file],
#   )
#
# - Strandsライブラリのログレベル制御（WARNING: 過剰なデバッグ出力を抑制）
#   logging.getLogger("strands").setLevel(logging.WARNING)


# ========== 以下、メイン関数 ==========
def main():
    """メイン関数"""
    _logger = logging.getLogger(__name__)

    # TODO: 詳細設計書に従い実装
    # - システム起動ログ出力
    #   _logger.info("システム起動")
    #
    # - OrchestratorAgentの生成と実行
    #   agent = OrchestratorAgent()
    #   agent.run()
    #
    # - 正常終了ログ出力
    #   _logger.info("システム正常終了")
    #
    # - エラーハンドリング（R9.1準拠）
    #   except KeyboardInterrupt:
    #       print(ErrorHandler.handle_keyboard_interrupt())
    #       _logger.info("システム終了（KeyboardInterrupt）")
    #   except Exception as e:
    #       _logger.error("システムエラー error=%s", str(e), exc_info=True)
    #       print(ErrorHandler.handle_unexpected_error(e))
    #       sys.exit(1)
    pass


if __name__ == "__main__":
    main()
```

## カスタマイズガイド

1. **ログ設定**: 3ハンドラー構成（console / app.log / error.log）を標準とする。`RotatingFileHandler` で 10MB × 5世代のローテーションを設定する
2. **Strandsログレベル**: `logging.getLogger("strands").setLevel(logging.WARNING)` でデバッグ出力を抑制する。DEBUGに変更するとReActループの詳細が確認できる
3. **ErrorHandler呼び出し**: インスタンス不要で `ErrorHandler.handle_xxx()` として直接呼び出す（R9.1参照）
4. **環境変数**: `.env.template` にプロジェクト固有の環境変数を追加する
