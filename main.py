"""申請受付窓口エージェント - メインエントリーポイント"""
import sys
import os
import logging
import warnings
from dotenv import load_dotenv
from agents.reception_agent import ReceptionAgent
from handlers.error_handler import ErrorHandler
from strands.types.exceptions import ModelThrottledException, MaxTokensReachedException

# .envファイルを読み込み
load_dotenv()


def _setup_logging():
    """ロギングの初期設定"""
    os.makedirs("logs", exist_ok=True)

    # .envのLOG_LEVELを読み取り、未設定の場合はWARNINGをデフォルトとする
    log_level_str = os.getenv("LOG_LEVEL", "WARNING").upper()
    log_level = getattr(logging, log_level_str, logging.WARNING)

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        handlers=[
            logging.FileHandler("logs/error.log", encoding="utf-8"),
            logging.StreamHandler(),  # コンソールにも出力
        ]
    )  

# ========== 以下、メイン関数 ==========
def main():
    # ロギングの初期設定
    _setup_logging()

    logger = logging.getLogger(__name__)

    # エラーハンドラーの初期化
    _error_handler = ErrorHandler()

    try:
        logger.info("システム起動")

        # エージェントの初期化
        agent = ReceptionAgent()

        # エージェントの実行
        agent.run()

        # エージェントの終了
        logger.info("システム正常終了")

    except KeyboardInterrupt:
        # キーボード中断（Ctrl+C）
        logger.info("ユーザーによる中断（KeyboardInterrupt）")
        user_message = _error_handler.handle_keyboard_interrupt()

        print("\n" + "=" * 60)
        print(f"\n{user_message}\n")
        print("=" * 60)
        sys.exit(0)

    except ModelThrottledException as e:
        # APIレート制限エラー
        logger.error(f"ModelThrottledException: {str(e)}")
        user_message = _error_handler.handle_throttling_error(e)
        print("\n" + "=" * 60)
        print(f"\n{user_message}\n")
        print("=" * 60)
        sys.exit(1)

    except MaxTokensReachedException as e:
        # 最大トークン数到達エラー
        logger.error(f"MaxTokensReachedException: {str(e)}")
        user_message = _error_handler.handle_max_tokens_error(e)
        print("\n" + "=" * 60)
        print(f"\n{user_message}\n")
        print("=" * 60)
        sys.exit(1)

    except RuntimeError as e:
        # その他のRuntimeError
        logger.error(f"RuntimeError が発生しました: {str(e)[:100]}", exc_info=True)
        user_message = _error_handler.handle_runtime_error(e)

        print("\n" + "=" * 60)
        print(f"\n{user_message}\n")
        print("=" * 60)
        sys.exit(1)

    except Exception as e:
        # その他のすべてのエラー
        logger.error(f"予期しないエラーが発生しました: {type(e).__name__}: {str(e)}", exc_info=True)
        user_message = _error_handler.handle_unexpected_error(e)

        print("\n" + "=" * 60)
        print(f"\n{user_message}\n")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()
