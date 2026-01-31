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
logging.getLogger("strands").setLevel(log_level)

# スタックトレースを抑制（エンドユーザー向けアプリケーション）
logging.getLogger("strands.event_loop.event_loop").setLevel(logging.CRITICAL)
warnings.filterwarnings("ignore")

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
    
    except KeyboardInterrupt:
        print("\n\nシステムを終了します。")
        error_handler.log_info("ユーザーによる中断")
        sys.exit(0)
    
    except RuntimeError as e:
        # ループ制限エラーの特別処理
        if "エージェントループの制限" in str(e):
            print("\n" + "=" * 60)
            print("【処理が複雑すぎます】")
            print("=" * 60)
            print("\n申し訳ございません。処理が複雑すぎて完了できませんでした。")
            print("\n以下のいずれかをお試しください：")
            print("1. タスクをより小さな単位に分割してください")
            print("   例：複数の申請を一度に行う場合は、1つずつ申請してください")
            print("2. より具体的な指示を提供してください")
            print("   例：「交通費を申請したい」→「1月10日の東京から大阪への新幹線代を申請したい」")
            print("3. 不要な情報を削除してください")
            print("   例：申請に関係のない質問や情報は別途お尋ねください")
            print("=" * 60)
            error_handler.log_error("LoopLimitError", str(e), {"error_type": "RuntimeError"}, exc_info=True)
            sys.exit(1)
        else:
            # その他のRuntimeError
            print("\n" + "=" * 60)
            print("【エラー】")
            print("=" * 60)
            print("\n予期しないエラーが発生しました。")
            print("システムを再起動してください。")
            print("\n問題が解決しない場合は、システム管理者にお問い合わせください。")
            print("=" * 60)
            error_handler.log_error("RuntimeError", str(e), {"error_type": "RuntimeError"}, exc_info=True)
            sys.exit(1)
    
    except FileNotFoundError as e:
        # ファイルが見つからないエラー
        print("\n" + "=" * 60)
        print("【ファイルエラー】")
        print("=" * 60)
        print("\n必要なファイルが見つかりません。")
        print("\n以下を確認してください：")
        print("1. dataフォルダに運賃データファイルが存在するか")
        print("2. outputフォルダが存在するか")
        print("\n問題が解決しない場合は、システム管理者にお問い合わせください。")
        print("=" * 60)
        error_handler.log_error("FileNotFoundError", str(e), {"error_type": "FileNotFoundError"}, exc_info=True)
        sys.exit(1)
    
    except PermissionError as e:
        # 権限エラー
        print("\n" + "=" * 60)
        print("【権限エラー】")
        print("=" * 60)
        print("\nファイルへのアクセス権限がありません。")
        print("\n以下を確認してください：")
        print("1. outputフォルダへの書き込み権限があるか")
        print("2. 管理者権限で実行する必要があるか")
        print("\n問題が解決しない場合は、システム管理者にお問い合わせください。")
        print("=" * 60)
        error_handler.log_error("PermissionError", str(e), {"error_type": "PermissionError"}, exc_info=True)
        sys.exit(1)
    
    except ConnectionError as e:
        # 接続エラー
        print("\n" + "=" * 60)
        print("【接続エラー】")
        print("=" * 60)
        print("\nAmazon Bedrockサービスへの接続に失敗しました。")
        print("\n以下を確認してください：")
        print("1. インターネット接続が正常か")
        print("2. AWS認証情報が正しく設定されているか")
        print("3. Amazon Bedrockへのアクセス権限があるか")
        print("\n問題が解決しない場合は、システム管理者にお問い合わせください。")
        print("=" * 60)
        error_handler.log_error("ConnectionError", str(e), {"error_type": "ConnectionError"}, exc_info=True)
        sys.exit(1)
    
    except ValueError as e:
        # 値エラー
        print("\n" + "=" * 60)
        print("【入力エラー】")
        print("=" * 60)
        print("\n入力データに問題があります。")
        print("\n正しい形式で再度入力してください。")
        print("\n問題が解決しない場合は、システム管理者にお問い合わせください。")
        print("=" * 60)
        error_handler.log_error("ValueError", str(e), {"error_type": "ValueError"}, exc_info=True)
        sys.exit(1)
    
    except Exception as e:
        # その他のすべてのエラー
        error_type = type(e).__name__
        
        print("\n" + "=" * 60)
        print("【予期しないエラー】")
        print("=" * 60)
        print("\n予期しないエラーが発生しました。")
        print("システムを再起動してください。")
        print("\n問題が解決しない場合は、以下の情報をシステム管理者に伝えてください：")
        print(f"エラータイプ: {error_type}")
        print("=" * 60)
        error_handler.log_error("UnexpectedError", str(e), {"error_type": error_type}, exc_info=True)
        
        sys.exit(1)


if __name__ == "__main__":
    main()
