"""申請受付窓口エージェント - メインエントリーポイント"""
import sys
import os
import logging
import warnings
from dotenv import load_dotenv
from agents.reception_agent import ReceptionAgent
from handlers.error_handler import ErrorHandler


# .envファイルを読み込み
load_dotenv()

# logger設定
log_level = os.getenv("LOG_LEVEL", "INFO")

# ログディレクトリの作成
os.makedirs("logs", exist_ok=True)

# 基本設定
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    level=log_level,
    handlers=[
        logging.StreamHandler(),  # コンソール出力
        logging.FileHandler("logs/error.log", encoding="utf-8")  # ファイル出力
    ]
)

# AWS Strandsライブラリの制御
logging.getLogger("strands").setLevel(log_level)

# スタックトレースを抑制（エンドユーザー向けアプリケーション）
logging.getLogger("strands.event_loop.event_loop").setLevel(logging.CRITICAL)

# 警告メッセージを非表示
warnings.filterwarnings("ignore")


# ========== 以下、メイン関数==========
def main():
    # エラーハンドラーの初期化
    error_handler = ErrorHandler()
    
    try:
        error_handler.log_info("システム起動")

        # エージェントの初期化
        agent = ReceptionAgent()
        
        # エージェントの実行
        agent.run()

        # エージェントの終了
        error_handler.log_info("システム正常終了")
    
    except KeyboardInterrupt:
        print("\n\nシステムを終了します。")
        error_handler.log_info("ユーザーによる中断")
        sys.exit(0)
    

    except RuntimeError as e:
        # ループ制限エラーの特別処理
        if "エージェントループの制限" in str(e):
            user_message = error_handler.handle_loop_limit_error(e, {"error_type": "RuntimeError"})
            print(user_message)
            sys.exit(1)
        else:
            # その他のRuntimeError
            error_handler.log_error("RuntimeError", str(e), {"error_type": "RuntimeError"}, exc_info=True)
            print("\n" + "=" * 60)
            print("【エラー】")
            print("=" * 60)
            print("\n予期しないエラーが発生しました。")
            print("システムを再起動してください。")
            print("\n問題が解決しない場合は、システム管理者にお問い合わせください。")
            print("=" * 60)
            sys.exit(1)
    
    
    except ConnectionError as e:
        # 接続エラー
        user_message = error_handler.handle_bedrock_error(e, {"error_type": "ConnectionError"})
        print(user_message)
        sys.exit(1)
    
    
    except Exception as e:
        # その他のすべてのエラー
        error_type = type(e).__name__
        error_handler.log_error("UnexpectedError", str(e), {"error_type": error_type}, exc_info=True)
        
        print("\n" + "=" * 60)
        print("【予期しないエラー】")
        print("=" * 60)
        print("\n予期しないエラーが発生しました。")
        print("システムを再起動してください。")
        print("\n問題が解決しない場合は、以下の情報をシステム管理者に伝えてください：")
        print(f"エラータイプ: {error_type}")
        print("=" * 60)
        
        sys.exit(1)


if __name__ == "__main__":
    main()
