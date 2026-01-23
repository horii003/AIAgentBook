"""社内申請の代行エージェント - メインエントリーポイント"""
import sys
from config.config_manager import ConfigManager
from tools.config_update import set_config_manager
from agents.reception_agent import ReceptionAgent
from handlers.error_handler import ErrorHandler


def main():
    # エラーハンドラーの初期化
    error_handler = ErrorHandler()
    
    try:
        error_handler.log_info("システム起動")
        
        # ConfigManagerの初期化
        config_manager = ConfigManager()
        
        # ConfigManagerをconfig_updateツールに設定
        set_config_manager(config_manager)
        
        # エージェントの初期化
        agent = ReceptionAgent()
        
        # エージェントの実行
        agent.run()

        # エージェントの終了
        error_handler.log_info("システム正常終了")

    #必要か確認    
    except FileNotFoundError as e:
        # 運賃データファイルが見つからない
        print("\n" + "=" * 60)
        print("エラー")
        print("=" * 60)
        print(error_handler.handle_fare_data_error(e))
        print("=" * 60)
        sys.exit(1)
    
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
