"""シンプルなログ機能付きステアリングハンドラー"""

import sys
import os
import logging
from dotenv import load_dotenv
from strands.experimental.steering import LLMSteeringHandler

# .envファイルを読み込み
load_dotenv()

log_level = os.environ['LOG_LEVEL'] if os.environ['LOG_LEVEL'] is None else "INFO"

# ステアリングハンドラー用のロガー設定
def setup_steering_logger():
    """ステアリングハンドラー用のシンプルなロガーをセットアップ"""
    logger = logging.getLogger("SteeringHandler")
    logger.setLevel(log_level)
    
    # 既存のハンドラーをクリア
    if logger.handlers:
        logger.handlers.clear()
    
    # コンソール出力
    console_handler = logging.StreamHandler()
    # console_handler.setLevel(logging.INFO)
    
    # ファイル出力
    file_handler = logging.FileHandler("logs/steering.log", encoding="utf-8")
    # file_handler.setLevel(logging.INFO)
    
    # フォーマット（詳細フォーマットで統一）
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s - %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger


# グローバルロガー
steering_logger = setup_steering_logger()


def log_steering_decision(decision: str, reason: str):
    """
    ステアリングハンドラーの判断をログ出力
    
    Args:
        decision: 判断結果（proceed/guide/interrupt）
        reason: 判断理由
    """
    message = f"[STEERING] {decision.upper()}: {reason}"
    
    if decision.lower() == "interrupt":
        steering_logger.warning(message)
    else:
        steering_logger.info(message)


class LoggedSteeringHandler(LLMSteeringHandler):
    """シンプルなログ機能付きステアリングハンドラー"""
    
    def __call__(self, *args, **kwargs):
        """ステアリングハンドラーの実行とログ出力"""
        try:
            # 親クラスのメソッドを実行
            result = super().__call__(*args, **kwargs)
            
            # 結果をログ出力
            result_str = str(result)
            
            # 判断結果を解析してログ出力
            if "proceed" in result_str.lower():
                decision = "proceed"
                reason = result_str.split(":", 1)[1].strip() if ":" in result_str else result_str
            elif "guide" in result_str.lower():
                decision = "guide"
                reason = result_str.split(":", 1)[1].strip() if ":" in result_str else result_str
            elif "interrupt" in result_str.lower():
                decision = "interrupt"
                reason = result_str.split(":", 1)[1].strip() if ":" in result_str else result_str
            else:
                decision = "unknown"
                reason = result_str
            
            log_steering_decision(decision, reason)
            
            return result
            
        except Exception as e:
            steering_logger.error(f"[STEERING ERROR] {str(e)}")
            raise

