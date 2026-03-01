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

# ログディレクトリの作成
os.makedirs("logs", exist_ok=True)

# ファイル用ハンドラー（WARNING以上のみ、コンソール出力なし）
_file_handler = logging.FileHandler("logs/error.log", encoding="utf-8")
_file_handler.setLevel(logging.WARNING)
_file_handler.setFormatter(logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
))

# 基本設定
logging.basicConfig(
    level=logging.WARNING,
    handlers=[_file_handler]  # ファイル出力のみ
)

# AWS Strandsライブラリの制御
logging.getLogger("strands").setLevel(logging.WARNING)

# スタックトレースを抑制（エンドユーザー向けアプリケーション）
logging.getLogger("strands.event_loop.event_loop").setLevel(logging.CRITICAL)

# 警告メッセージを非表示
warnings.filterwarnings("ignore")


# ========== 以下、メイン関数==========
def main():
    # エラーハンドラーの初期化
    _error_handler = ErrorHandler()
    
    try:
        _error_handler.log_info("システム起動")

        # エージェントの初期化
        agent = ReceptionAgent()
        
        # エージェントの実行
        agent.run()

        # エージェントの終了
        _error_handler.log_info("システム正常終了")
    
    except KeyboardInterrupt:
        # キーボード中断（Ctrl+C）
        user_message = _error_handler.handle_keyboard_interrupt()
        
        print("\n" + "=" * 60)
        print(f"\n{user_message}\n")
        print("=" * 60)
        sys.exit(0)
    
    except RuntimeError as e:
        # その他のRuntimeError
        user_message = _error_handler.handle_runtime_error(
            error=e,
            agent_name="main",
            context={"error_type": "RuntimeError"}
        )
        
        print("\n" + "=" * 60)
        print(f"\n{user_message}\n")
        print("=" * 60)
        sys.exit(1)
    
    
    except ConnectionError as e:
        # 接続エラー
        user_message = _error_handler.handle_bedrock_error(
            e, 
            {"error_type": "ConnectionError"}
        )
        print("\n" + "=" * 60)
        print(f"\n{user_message}\n")
        print("=" * 60)
        sys.exit(1)
    
    except Exception as e:
        # その他のすべてのエラー
        user_message = _error_handler.handle_unexpected_error(
            e,
            agent_name="main",
            context={"error_type": type(e).__name__}
        )
        
        print("\n" + "=" * 60)
        print(f"\n{user_message}\n")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()
