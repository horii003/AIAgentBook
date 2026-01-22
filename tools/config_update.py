"""
設定更新ツール

システム設定（申請者名、出力ディレクトリ）を更新します。
"""

from strands import tool


# グローバル変数としてConfigManagerインスタンスを保持
# エージェント初期化時に設定される
_config_manager = None


def set_config_manager(config_manager):
    """
    ConfigManagerインスタンスを設定
    
    Args:
        config_manager: ConfigManagerインスタンス
    """
    global _config_manager
    _config_manager = config_manager


@tool
def config_updater(setting_name: str, setting_value: str) -> str:
    """
    システム設定を更新する。
    
    このツールは申請者名や出力ディレクトリなどの設定を変更します。
    
    使用可能な設定：
    - applicant_name: 申請者名を変更
    - output_directory: 出力ディレクトリのパスを変更
    
    使用例：
    - ユーザーが「申請者は田中太郎です」と入力した場合
      → setting_name="applicant_name", setting_value="田中太郎"
    - ユーザーが「出力先を./reports に変更」と入力した場合
      → setting_name="output_directory", setting_value="./reports"
    
    Args:
        setting_name: 設定名（「applicant_name」または「output_directory」）
        setting_value: 設定値
        
    Returns:
        str: 設定変更の確認メッセージ
        
    Raises:
        ValueError: 無効な設定名が指定された場合
        RuntimeError: ConfigManagerが初期化されていない場合
    """
    if _config_manager is None:
        raise RuntimeError("ConfigManagerが初期化されていません")
    
    if setting_name == "applicant_name":
        _config_manager.set_applicant_name(setting_value)
        return f"申請者名を「{setting_value}」に更新しました"
    elif setting_name == "output_directory":
        _config_manager.set_output_directory(setting_value)
        return f"出力ディレクトリを「{setting_value}」に更新しました"
    else:
        raise ValueError(f"無効な設定名です: {setting_name}。使用可能な設定: applicant_name, output_directory")
