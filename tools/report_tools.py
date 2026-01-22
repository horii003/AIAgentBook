"""申請書生成関連のツール"""
import json
import os
from datetime import datetime
from typing import List
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
from strands import Agent,tool


@tool
def generate_report(
    routes: List[dict],
    format: str,
    user_id: str = "0001"
) -> dict:
    """
    交通費申請書を生成して保存します。
    
    Args:
        routes: 経路データのリスト。各要素は以下のキーを持つ辞書:
            - departure (str): 出発地
            - destination (str): 目的地
            - date (str): 日付
            - transport_type (str): 交通手段 (train/bus/taxi/airplane)
            - cost (float): 費用
            - notes (str, optional): 備考
        format: 出力形式（pdf/json）
        user_id: ユーザー識別子（デフォルト: "0001"）
    
    Returns:
        dict: {
            "success": bool,         # 成功フラグ
            "file_path": str,        # 保存されたファイルのパス
            "total_cost": float,     # 合計経費
            "message": str           # 結果メッセージ
        }
    """
    try:
        # 入力検証
        if not routes:
            return {
                "success": False,
                "file_path": "",
                "total_cost": 0,
                "message": "エラー: 経路データが空です"
            }
        
        # routesがリストでない場合の処理
        if not isinstance(routes, list):
            return {
                "success": False,
                "file_path": "",
                "total_cost": 0,
                "message": f"エラー: routesはリストである必要があります（受信: {type(routes).__name__}）"
            }
        
        # 各経路データの検証
        required_keys = ["departure", "destination", "transport_type", "cost"]
        for i, route in enumerate(routes):
            if not isinstance(route, dict):
                return {
                    "success": False,
                    "file_path": "",
                    "total_cost": 0,
                    "message": f"エラー: 経路{i+1}が辞書形式ではありません"
                }
            
            missing_keys = [key for key in required_keys if key not in route]
            if missing_keys:
                return {
                    "success": False,
                    "file_path": "",
                    "total_cost": 0,
                    "message": f"エラー: 経路{i+1}に必須キーが不足しています: {missing_keys}"
                }
        
        # 形式の正規化と検証
        format = format.lower().strip()
        if format not in ["pdf", "json"]:
            return {
                "success": False,
                "file_path": "",
                "total_cost": 0,
                "message": f"エラー: 無効な形式です: {format}。有効な値: pdf, json"
            }
        
        # 合計経費の計算
        total_cost = sum(float(route.get("cost", 0)) for route in routes)
        
        # ファイル名の生成（日付とユーザーIDを含む）
        now = datetime.now()
        date_str = now.strftime("%Y%m%d_%H%M%S")
        filename = f"expense_report_{user_id}_{date_str}"
        
        # 出力フォルダの確認
        output_dir = "output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 形式に応じて生成
        if format == "pdf":
            file_path = os.path.join(output_dir, f"{filename}.pdf")
            _generate_pdf(routes, total_cost, user_id, now, file_path)
        else:  # json
            file_path = os.path.join(output_dir, f"{filename}.json")
            _generate_json(routes, total_cost, user_id, now, file_path)
        
        return {
            "success": True,
            "file_path": file_path,
            "total_cost": total_cost,
            "message": f"申請書を正常に作成しました: {file_path}"
        }
    
    except Exception as e:
        return {
            "success": False,
            "file_path": "",
            "total_cost": 0,
            "message": f"エラー: {str(e)}"
        }


def _generate_pdf(routes: List[dict], total_cost: float, user_id: str, report_date: datetime, file_path: str):
    """
    PDF形式の申請書を生成
    
    Args:
        routes: 経路データのリスト
        total_cost: 合計経費
        user_id: ユーザーID
        report_date: 申請日
        file_path: 保存先ファイルパス
    """
    try:
        # PDFキャンバスの作成
        c = canvas.Canvas(file_path, pagesize=A4)
        width, height = A4
        
        # 日本語フォントの設定
        font_name = _register_japanese_font()
        
        # タイトル
        c.setFont(font_name, 16)
        c.drawString(50*mm, height - 30*mm, "交通費申請書")
        
        # 申請者情報
        c.setFont(font_name, 12)
        c.drawString(30*mm, height - 45*mm, f"申請者ID: {user_id}")
        c.drawString(30*mm, height - 52*mm, f"申請日: {report_date.strftime('%Y年%m月%d日')}")
        
        # 区切り線
        c.line(30*mm, height - 58*mm, width - 30*mm, height - 58*mm)
        
        # 経路一覧のヘッダー
        y_position = height - 70*mm
        c.setFont(font_name, 12)
        c.drawString(30*mm, y_position, "経路一覧:")
        
        # 各経路の詳細
        c.setFont(font_name, 10)
        y_position -= 10*mm
        
        for i, route in enumerate(routes, 1):
            # ページの下部に近づいたら改ページ
            if y_position < 40*mm:
                c.showPage()
                c.setFont(font_name, 10)
                y_position = height - 30*mm
            
            # 経路番号
            c.drawString(30*mm, y_position, f"{i}.")
            y_position -= 5*mm
            
            # 日付
            route_date = route.get("date", "")
            c.drawString(35*mm, y_position, f"日付: {route_date}")
            y_position -= 5*mm
            
            # 出発地 → 目的地
            c.drawString(35*mm, y_position, f"経路: {route['departure']} → {route['destination']}")
            y_position -= 5*mm
            
            # 交通手段
            transport_map = {
                "train": "電車",
                "bus": "バス",
                "taxi": "タクシー",
                "airplane": "飛行機"
            }
            transport_name = transport_map.get(route['transport_type'], route['transport_type'])
            c.drawString(35*mm, y_position, f"交通手段: {transport_name}")
            y_position -= 5*mm
            
            # 費用
            c.drawString(35*mm, y_position, f"費用: ¥{route['cost']:,.0f}")
            y_position -= 5*mm
            
            # 備考（あれば）
            if route.get('notes'):
                c.drawString(35*mm, y_position, f"備考: {route['notes']}")
                y_position -= 5*mm
            
            y_position -= 3*mm  # 経路間のスペース
        
        # 区切り線
        y_position -= 5*mm
        c.line(30*mm, y_position, width - 30*mm, y_position)
        
        # 合計経費
        y_position -= 10*mm
        c.setFont(font_name, 14)
        c.drawString(30*mm, y_position, f"合計経費: ¥{total_cost:,.0f}")
        
        # PDFの保存
        c.save()
        
    except Exception as e:
        raise IOError(f"PDF生成中にエラーが発生しました: {e}")


def _register_japanese_font():
    """
    日本語フォントを登録して、フォント名を返す
    
    Returns:
        str: 登録されたフォント名
    """
    import sys
    import platform
    
    # 既に登録済みの場合はスキップ
    try:
        if 'JapaneseFont' in pdfmetrics.getRegisteredFontNames():
            return 'JapaneseFont'
    except:
        pass
    
    # Windowsの場合
    if platform.system() == 'Windows':
        font_paths = [
            r'C:\Windows\Fonts\msgothic.ttc',  # MSゴシック
            r'C:\Windows\Fonts\msmincho.ttc',  # MS明朝
            r'C:\Windows\Fonts\meiryo.ttc',    # メイリオ
            r'C:\Windows\Fonts\YuGothM.ttc',   # 游ゴシック Medium
        ]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    # TTCファイルの場合はサブフォントインデックスを指定
                    pdfmetrics.registerFont(TTFont('JapaneseFont', font_path, subfontIndex=0))
                    return 'JapaneseFont'
                except Exception as e:
                    print(f"フォント登録失敗 ({font_path}): {e}")
                    continue
    
    # Macの場合
    elif platform.system() == 'Darwin':
        font_paths = [
            '/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc',
            '/Library/Fonts/Osaka.ttf',
        ]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    pdfmetrics.registerFont(TTFont('JapaneseFont', font_path))
                    return 'JapaneseFont'
                except Exception as e:
                    print(f"フォント登録失敗 ({font_path}): {e}")
                    continue
    
    # フォントが見つからない場合の警告
    print("警告: 日本語フォントが見つかりませんでした。デフォルトフォントを使用します。")
    return 'Helvetica'


def _generate_json(routes: List[dict], total_cost: float, user_id: str, report_date: datetime, file_path: str):
    """
    JSON形式の申請書を生成
    
    Args:
        routes: 経路データのリスト
        total_cost: 合計経費
        user_id: ユーザーID
        report_date: 申請日
        file_path: 保存先ファイルパス
    """
    try:
        # JSON構造の作成
        report_data = {
            "user_id": user_id,
            "report_date": report_date.strftime("%Y-%m-%d"),
            "routes": routes,
            "total_cost": total_cost
        }
        
        # JSONファイルの保存
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
    
    except Exception as e:
        raise IOError(f"JSON生成中にエラーが発生しました: {e}")
