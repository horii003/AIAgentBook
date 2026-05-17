"""アプリケーションエントリーポイント

経費精算・交通費精算申請エージェントシステムのメインモジュール。
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

from dotenv import load_dotenv

from agents.orchestrator_agent import OrchestratorAgent
from handlers.error_handler import ErrorHandler

_logger = logging.getLogger(__name__)

_LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
_LOG_DIR = Path("logs")
_LOG_FILE = _LOG_DIR / "app.log"
_ERROR_LOG_FILE = _LOG_DIR / "error.log"


def _setup_logging() -> None:
    """ログ設定を構成する"""
    _LOG_DIR.mkdir(parents=True, exist_ok=True)

    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level, logging.INFO))

    # コンソールハンドラー
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(_LOG_FORMAT))
    root_logger.addHandler(console_handler)

    # アプリログハンドラー（INFO以上）
    app_handler = RotatingFileHandler(
        str(_LOG_FILE), maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    app_handler.setLevel(logging.INFO)
    app_handler.setFormatter(logging.Formatter(_LOG_FORMAT))
    root_logger.addHandler(app_handler)

    # エラーログハンドラー（ERROR以上）
    error_handler = RotatingFileHandler(
        str(_ERROR_LOG_FILE), maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter(_LOG_FORMAT))
    root_logger.addHandler(error_handler)

    # Strandsイベントループログレベル制御
    logging.getLogger("strands").setLevel(logging.WARNING)


def main() -> None:
    """メイン関数"""
    load_dotenv()
    _setup_logging()

    _logger.info("アプリケーション起動")

    try:
        applicant_name = input("申請者名を入力してください: ").strip()
        if not applicant_name:
            applicant_name = "未入力"

        agent = OrchestratorAgent(applicant_name=applicant_name)
        agent.run()
    except KeyboardInterrupt:
        print(f"\n{ErrorHandler.handle_keyboard_interrupt(KeyboardInterrupt())}")
    except Exception as e:
        _logger.error("アプリケーションエラー: %s", e, exc_info=True)
        print(ErrorHandler.handle_unexpected_error(e))
    finally:
        _logger.info("アプリケーション終了")


if __name__ == "__main__":
    main()
