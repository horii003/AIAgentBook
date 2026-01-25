"""運賃計算関連のツール"""
import json
import os
from typing import Dict, List
from strands import Agent,tool


# グローバル変数として運賃データを保持
_fare_data_cache = None


@tool
def load_fare_data() -> dict:
    """
    dataフォルダから運賃データを読み込みます。
    
    Returns:
        dict: {
            "train_fares": List[dict],  # 電車の運賃テーブル
            "fixed_fares": dict          # バス、タクシー、飛行機の固定運賃
        }
    
    Raises:
        FileNotFoundError: 運賃データファイルが見つからない場合
        ValueError: データ形式が不正な場合
    """
    global _fare_data_cache
    
    # キャッシュがあれば返す
    if _fare_data_cache is not None:
        return _fare_data_cache
    
    # ファイルパスの設定
    train_fares_path = os.path.join("data", "train_fares.json")
    fixed_fares_path = os.path.join("data", "fixed_fares.json")
    
    # ファイルの存在確認
    if not os.path.exists(train_fares_path):
        raise FileNotFoundError(f"電車運賃データファイルが見つかりません: {train_fares_path}")
    
    if not os.path.exists(fixed_fares_path):
        raise FileNotFoundError(f"固定運賃データファイルが見つかりません: {fixed_fares_path}")
    
    try:
        # 電車運賃データの読み込みと変換
        with open(train_fares_path, "r", encoding="utf-8") as f:
            train_data = json.load(f)
        
        # 固定運賃データの読み込みと変換
        with open(fixed_fares_path, "r", encoding="utf-8") as f:
            fixed_data = json.load(f)
        
        # データ形式の検証
        if "routes" not in train_data:
            raise ValueError("電車運賃データに'routes'キーが存在しません")
        
        if not isinstance(train_data["routes"], list):
            raise ValueError("電車運賃データの'routes'はリストである必要があります")
        
        # 各経路データの検証
        for route in train_data["routes"]:
            if not all(key in route for key in ["departure", "destination", "fare"]):
                raise ValueError("電車運賃データの各経路には'departure', 'destination', 'fare'が必要です")
        
        # 固定運賃データの検証
        required_transport_types = ["bus", "taxi", "airplane"]
        for transport_type in required_transport_types:
            if transport_type not in fixed_data:
                raise ValueError(f"固定運賃データに'{transport_type}'が存在しません")
        
        # データをキャッシュ
        _fare_data_cache = {
            "train_fares": train_data["routes"],
            "fixed_fares": fixed_data
        }
        
        return _fare_data_cache
    
    except json.JSONDecodeError as e:
        raise ValueError(f"JSONファイルの解析に失敗しました: {e}")
    except Exception as e:
        raise ValueError(f"運賃データの読み込み中にエラーが発生しました: {e}")


@tool
def calculate_fare(
    departure: str,
    destination: str,
    transport_type: str,
    date: str
) -> dict:
    """
    経路の交通費を計算します。
    
    Args:
        departure: 出発地
        destination: 目的地
        transport_type: 交通手段（train/bus/taxi/airplane）
        date: 移動日（YYYY-MM-DD形式）
    
    Returns:
        dict: {
            "fare": float,           # 計算された運賃
            "calculation_method": str # 計算方法の説明
        }
    
    Raises:
        ValueError: 経路が運賃データに存在しない場合
    """
    # 運賃データの読み込み
    fare_data = load_fare_data()
    
    # 交通手段の正規化（小文字に変換）
    transport_type = transport_type.lower()
    
    # 交通手段の検証
    valid_transport_types = ["train", "bus", "taxi", "airplane"]
    if transport_type not in valid_transport_types:
        raise ValueError(f"無効な交通手段です: {transport_type}。有効な値: {', '.join(valid_transport_types)}")
    
    # 電車の場合
    if transport_type == "train":
        # 運賃テーブルから該当する経路を検索
        for route in fare_data["train_fares"]:
            if route["departure"] == departure and route["destination"] == destination:
                return {
                    "fare": float(route["fare"]),
                    "calculation_method": f"電車運賃テーブルから取得: {departure} → {destination}"
                }
        
        # 経路が見つからない場合
        raise ValueError(f"電車の運賃データに該当する経路が見つかりません: {departure} → {destination}")
    
    # バス、タクシー、飛行機の場合（固定運賃）
    else:
        fare = fare_data["fixed_fares"][transport_type]
        transport_name_map = {
            "bus": "バス",
            "taxi": "タクシー",
            "airplane": "飛行機"
        }
        return {
            "fare": float(fare),
            "calculation_method": f"{transport_name_map[transport_type]}の固定運賃"
        }
