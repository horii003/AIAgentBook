"""マルチエージェントアプリケーション - メインエントリーポイント"""
import sys
import os
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
from agents.orchestrator_agent import OrchestratorAgent
from handlers.error_handler import ErrorHandler
from session.session_manager import SessionManagerFactory


# .envファイルを読み込み
load_dotenv()

# ログレベルの取得
log_level = getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO)

# ログディレクトリの作成
os.makedirs("logs", exist_ok=True)

# ログフォーマッターの作成
_fmt = "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
_formatter = logging.Formatter(_fmt)

# app.log ハンドラー（INFO以上、RotatingFileHandler: 10MB × 5世代）
_app_handler = RotatingFileHandler(
    "logs/app.log", maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
)
_app_handler.setLevel(logging.INFO)
_app_handler.setFormatter(_formatter)

# error.log ハンドラー（ERROR以上、RotatingFileHandler: 10MB × 5世代）
_error_handler_file = RotatingFileHandler(
    "logs/error.log", maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
)
_error_handler_file.setLevel(logging.ERROR)
_error_handler_file.setFormatter(_formatter)

# コンソールハンドラー（INFO以上）
_console_handler = logging.StreamHandler()
_console_handler.setLevel(logging.INFO)
_console_handler.setFormatter(_formatter)

# logging.basicConfigの設定（3ハンドラー構成）
logging.basicConfig(
    level=log_level,
    handlers=[_console_handler, _app_handler, _error_handler_file],
)

# Strandsライブラリのログレベル制御（WARNING: 過剰なデバッグ出力を抑制）
logging.getLogger("strands").setLevel(logging.WARNING)


def main():
    """メイン関数"""
    _logger = logging.getLogger(__name__)
    _logger.info("システム起動")

    try:
        session_id = SessionManagerFactory.generate_session_id()
        agent = OrchestratorAgent(session_id=session_id)
        agent.run()
        _logger.info("システム正常終了")
    except KeyboardInterrupt:
        print(ErrorHandler.handle_keyboard_interrupt())
        _logger.info("システム終了（KeyboardInterrupt）")
    except Exception as e:
        _logger.error("システムエラー error=%s", str(e), exc_info=True)
        print(ErrorHandler.handle_unexpected_error(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
