"""マルチエージェントアプリケーション - メインエントリーポイント

経費・交通費精算申請支援システムのエントリーポイント。
"""
import sys
import os
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv

# .envファイルを読み込み
load_dotenv()

# ログ設定
_log_level = getattr(logging, os.getenv("LOG_LEVEL", "WARNING").upper(), logging.WARNING)
os.makedirs("logs", exist_ok=True)

_fmt = "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
_formatter = logging.Formatter(_fmt)

_app_handler = RotatingFileHandler(
    "logs/app.log", maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
)
_app_handler.setLevel(logging.INFO)
_app_handler.setFormatter(_formatter)

_error_handler_file = RotatingFileHandler(
    "logs/error.log", maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
)
_error_handler_file.setLevel(logging.ERROR)
_error_handler_file.setFormatter(_formatter)

_console_handler = logging.StreamHandler()
_console_handler.setLevel(logging.INFO)
_console_handler.setFormatter(_formatter)

logging.basicConfig(
    level=_log_level,
    handlers=[_console_handler, _app_handler, _error_handler_file],
)

# Strandsライブラリのログレベル制御（過剰なデバッグ出力を抑制）
logging.getLogger("strands").setLevel(logging.WARNING)

_logger = logging.getLogger(__name__)


def main() -> None:
    """メイン関数。申請者名を取得してオーケストレーターエージェントを起動する。"""
    from agents.orchestrator_agent import OrchestratorAgent
    from handlers.error_handler import ErrorHandler
    from session.session_manager import SessionManagerFactory

    _logger.info("システム起動")

    try:
        applicant_name = input("申請者名を入力してください: ").strip()
        session_id = SessionManagerFactory.generate_session_id()
        _logger.info("セッション開始: session_id=%s, applicant_name=%s", session_id, applicant_name)

        OrchestratorAgent(applicant_name=applicant_name, session_id=session_id).run()
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
