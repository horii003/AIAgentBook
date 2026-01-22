"""入力検証関連のツール"""
from datetime import datetime
from dateutil import parser
from strands import Agent,tool
from tools.fare_tools import load_fare_data


@tool
def validate_input(
    input_type: str,
    value: str
) -> dict:
    """
    入力データを検証します。
    
    Args:
        input_type: 検証タイプ（date/location/amount）
        value: 検証する値
    
    Returns:
        dict: {
            "valid": bool,           # 検証結果
            "error_message": str     # エラーメッセージ（無効な場合）
        }
    """
    input_type = input_type.lower()
    
    if input_type == "date":
        return _validate_date(value)
    elif input_type == "location":
        return _validate_location(value)
    elif input_type == "amount":
        return _validate_amount(value)
    else:
        return {
            "valid": False,
            "error_message": f"無効な検証タイプです: {input_type}。有効な値: date, location, amount"
        }


def _validate_date(date_str: str) -> dict:
    """
    日付の検証
    
    Args:
        date_str: 日付文字列
    
    Returns:
        dict: 検証結果
    """
    try:
        # 日付のパース
        parsed_date = parser.parse(date_str)
        
        # 妥当な範囲の確認（過去1年から未来1年まで）
        now = datetime.now()
        one_year_ago = datetime(now.year - 1, now.month, now.day)
        one_year_later = datetime(now.year + 1, now.month, now.day)
        
        if parsed_date < one_year_ago:
            return {
                "valid": False,
                "error_message": f"日付が古すぎます: {date_str}。過去1年以内の日付を入力してください。"
            }
        
        if parsed_date > one_year_later:
            return {
                "valid": False,
                "error_message": f"日付が未来すぎます: {date_str}。1年以内の日付を入力してください。"
            }
        
        return {
            "valid": True,
            "error_message": ""
        }
    
    except (ValueError, parser.ParserError) as e:
        return {
            "valid": False,
            "error_message": f"無効な日付形式です: {date_str}。YYYY-MM-DD形式で入力してください。"
        }


def _validate_location(location: str) -> dict:
    """
    場所の検証
    
    Args:
        location: 場所名
    
    Returns:
        dict: 検証結果
    """
    # 空文字チェック
    if not location or location.strip() == "":
        return {
            "valid": False,
            "error_message": "場所が入力されていません。"
        }
    
    # 運賃データを読み込んで、認識可能な場所かチェック
    try:
        fare_data = load_fare_data()
        
        # 電車の運賃テーブルから場所のリストを作成
        valid_locations = set()
        for route in fare_data["train_fares"]:
            valid_locations.add(route["departure"])
            valid_locations.add(route["destination"])
        
        # 場所が認識可能かチェック
        if location not in valid_locations:
            return {
                "valid": False,
                "error_message": f"認識できない場所です: {location}。運賃データに登録されている場所を入力してください。"
            }
        
        return {
            "valid": True,
            "error_message": ""
        }
    
    except Exception as e:
        # 運賃データの読み込みに失敗した場合は、とりあえず有効とする
        return {
            "valid": True,
            "error_message": ""
        }


def _validate_amount(amount_str: str) -> dict:
    """
    金額の検証
    
    Args:
        amount_str: 金額文字列
    
    Returns:
        dict: 検証結果
    """
    try:
        # 数値に変換
        amount = float(amount_str)
        
        # 正の数かチェック
        if amount <= 0:
            return {
                "valid": False,
                "error_message": f"金額は正の数である必要があります: {amount_str}"
            }
        
        # 妥当な範囲かチェック（0円より大きく、100万円以下）
        if amount > 1000000:
            return {
                "valid": False,
                "error_message": f"金額が大きすぎます: {amount_str}。100万円以下の金額を入力してください。"
            }
        
        return {
            "valid": True,
            "error_message": ""
        }
    
    except ValueError:
        return {
            "valid": False,
            "error_message": f"無効な金額形式です: {amount_str}。数値を入力してください。"
        }
