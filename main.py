"""申請受付窓口エージェント - メインエントリーポイント"""
import sys
import logging
from config.config_manager import ConfigManager
from tools.config_update import set_config_manager
from agents.reception_agent import ReceptionAgent
from handlers.error_handler import ErrorHandler

# ConfigManagerの初期化
# config_manager = ConfigManager()
config_manager = ConfigManager.get_instance()

# ConfigManagerをconfig_updateツールに設定
set_config_manager(config_manager)

# logger
logging.getLogger("strands").setLevel(config_manager.log_level)
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    level=logging.INFO,
    handlers=[logging.StreamHandler()]
)

def main():
    # エラーハンドラーの初期化
    error_handler = ErrorHandler(log_level=config_manager.log_level)
    
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
