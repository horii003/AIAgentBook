"""申請受付窓口エージェント - メインエントリーポイント"""
import sys
import os
import logging
from dotenv import load_dotenv
from agents.reception_agent import ReceptionAgent
from handlers.error_handler import ErrorHandler

# .envファイルを読み込み
load_dotenv()

# logger
log_level = os.getenv("LOG_LEVEL", "INFO")
logging.getLogger("strands").setLevel(log_level)
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    level=log_level,
    handlers=[logging.StreamHandler()]
)

def main():
    # エラーハンドラーの初期化
    error_handler = ErrorHandler(log_level=log_level)
    
    try:
        error_handler.log_info("システム起動")

        # エージェントの初期化
        agent = ReceptionAgent()
        
        # エージェントの実行
        agent.run()

        # エージェントの終了
        error_handler.log_info("システム正常終了")
    
    except Exception as e:
        # その他のエラー
        error_type = type(e).__name__
        
        print("\n" + "=" * 60)
        print("エラー")
        print("=" * 60)
        print(f"予期しないエラーが発生しました: {e}")
        print(f"エラータイプ: {error_type}")
        print("=" * 60)
        error_handler.log_error("UnexpectedError", str(e), {"error_type": error_type})
        
        sys.exit(1)


if __name__ == "__main__":
    main()
