"""
Excel申請書生成ツール

Excel形式の経費精算申請書を生成します。
- 「経費精算申請エージェント(receipt_expense_agent)」：receipt_excel_generatorツールを利用
- 「交通費精算申請エージェント(travel_agent)」：travel_excel_generatorツールを利用

"""

from typing import List
from datetime import datetime
from pathlib import Path
from strands import tool
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from handlers.approval_rules import ApprovalRuleEngine


# 経費精算申請エージェント用の申請書作成ツール
@tool
def receipt_excel_generator(
    applicant_name: str,
    store_name: str,
    amount: float,
    date: str,
    items: List[str],
    expense_category: str
) -> dict:
    """
    Excel形式の経費精算申請書を生成する。

    経費精算申請エージェントが利用します。
    このツールは領収書データからExcel申請書を作成します。
    金額が30,000円を超える場合はエラーを返します。
    
    生成されるExcelファイルには以下の情報が含まれます：
    - 申請者名
    - 申請日（自動生成）
    - 店舗名
    - 金額
    - 購入日
    - 品目リスト
    - 経費区分
    - 承認状況
    
    ファイル名は「経費精算申請書_YYYYMMDD_HHMMSS.xlsx」の形式で生成されます。
    
    Args:
        applicant_name: 申請者名
        store_name: 店舗名
        amount: 金額（円）
        date: 日付（YYYY-MM-DD形式）
        items: 品目のリスト
        expense_category: 経費区分
        
    Returns:
        dict: {
            "success": bool,         # 成功フラグ
            "file_path": str,        # 保存されたファイルのパス
            "message": str           # 結果メッセージ
        }
        
    Raises:
        ValueError: 金額が30,000円を超える場合
    """
    # 金額チェック
    approved, message = ApprovalRuleEngine.check_amount(amount)
    if not approved:
        raise ValueError(message)
    
    # ファイル名の生成（タイムスタンプ付き）
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"経費精算申請書_{timestamp}.xlsx"
    
    # 出力ディレクトリの設定
    output_path = Path("output")
    output_path.mkdir(parents=True, exist_ok=True)
    
    # ファイルパスの生成
    file_path = output_path / filename
    

    # Excelワークブックの作成
    wb = Workbook()
    ws = wb.active
    ws.title = "経費精算申請書"
    
    # ヘッダースタイルの定義
    header_font = Font(bold=True, size=12)
    header_fill = PatternFill(start_color="CCE5FF", end_color="CCE5FF", fill_type="solid")
    center_alignment = Alignment(horizontal="center", vertical="center")
    
    # タイトル行
    ws["A1"] = "経費精算申請書"
    ws["A1"].font = Font(bold=True, size=14)
    ws["A1"].alignment = center_alignment
    ws.merge_cells("A1:B1")
    
    # 申請情報
    current_row = 3
    
    # 申請者名
    ws[f"A{current_row}"] = "申請者名"
    ws[f"A{current_row}"].font = header_font
    ws[f"A{current_row}"].fill = header_fill
    ws[f"B{current_row}"] = applicant_name
    current_row += 1
    
    # 申請日
    ws[f"A{current_row}"] = "申請日"
    ws[f"A{current_row}"].font = header_font
    ws[f"A{current_row}"].fill = header_fill
    ws[f"B{current_row}"] = datetime.now().strftime("%Y-%m-%d")
    current_row += 1
    
    # 空行
    current_row += 1
    
    # 領収書情報
    ws[f"A{current_row}"] = "店舗名"
    ws[f"A{current_row}"].font = header_font
    ws[f"A{current_row}"].fill = header_fill
    ws[f"B{current_row}"] = store_name
    current_row += 1
    
    ws[f"A{current_row}"] = "金額"
    ws[f"A{current_row}"].font = header_font
    ws[f"A{current_row}"].fill = header_fill
    ws[f"B{current_row}"] = f"¥{amount:,.0f}"
    current_row += 1
    
    ws[f"A{current_row}"] = "購入日"
    ws[f"A{current_row}"].font = header_font
    ws[f"A{current_row}"].fill = header_fill
    ws[f"B{current_row}"] = date
    current_row += 1
    
    ws[f"A{current_row}"] = "経費区分"
    ws[f"A{current_row}"].font = header_font
    ws[f"A{current_row}"].fill = header_fill
    ws[f"B{current_row}"] = expense_category
    current_row += 1
    
    # 品目リスト
    ws[f"A{current_row}"] = "品目"
    ws[f"A{current_row}"].font = header_font
    ws[f"A{current_row}"].fill = header_fill
    ws[f"B{current_row}"] = ", ".join(items)
    current_row += 1
    
    # 空行
    current_row += 1
    
    # 承認状況
    ws[f"A{current_row}"] = "承認状況"
    ws[f"A{current_row}"].font = header_font
    ws[f"A{current_row}"].fill = header_fill
    ws[f"B{current_row}"] = "承認"
    ws[f"B{current_row}"].font = Font(color="008000", bold=True)
    
    # 列幅の調整
    ws.column_dimensions["A"].width = 20
    ws.column_dimensions["B"].width = 40
    
    # ファイルの保存
    wb.save(file_path)
    
    return {
        "success": True,
        "file_path": str(file_path),
        "message": f"申請書を正常に作成しました: {file_path}"
    }


# 交通費精算申請エージェント用の申請書作成ツール
@tool
def travel_excel_generator(
    routes: List[dict],
    user_id: str = "0001"
) -> dict:

    """
    交通費申請書をExcel形式で生成する。

    交通費精算申請エージェントが利用します。
    このツールは交通費の経路データからExcel申請書を作成します。
    複数の経路を一覧表形式で表示し、合計交通費を計算します。
    
    Args:
        routes: 経路データのリスト。各要素は以下のキーを持つ辞書:
            - departure (str): 出発地
            - destination (str): 目的地
            - date (str): 日付（YYYY-MM-DD形式）
            - transport_type (str): 交通手段 (train/bus/taxi/airplane)
            - cost (float): 費用
            - notes (str, optional): 備考
        user_id: ユーザー識別子（デフォルト: "0001"）
    
    Returns:
        dict: {
            "success": bool,         # 成功フラグ
            "file_path": str,        # 保存されたファイルのパス
            "total_cost": float,     # 合計交通費
            "message": str           # 結果メッセージ
        }
    """

    try:
        #routesの事前検証
        if not routes:
            return {
                "success": False,
                "file_path": "",
                "total_cost": 0,
                "message": "エラー: 経路データが空です"
            }
        

        if not isinstance(routes, list):
            return {
                "success": False,
                "file_path": "",
                "total_cost": 0,
                "message": f"エラー: routesはリストである必要があります（受信: {type(routes).__name__}）"
            }
        

        #各経路データのチェック
        required_keys = ["departure", "destination", "transport_type", "cost"]
        for i, route in enumerate(routes):

            # 辞書型かチェック
            if not isinstance(route, dict):
                return {
                    "success": False,
                    "file_path": "",
                    "total_cost": 0,
                    "message": f"エラー: 経路{i+1}が辞書形式ではありません"
                }

            #必須キーの確認
            missing_keys = [key for key in required_keys if key not in route]
            if missing_keys:
                return {
                    "success": False,
                    "file_path": "",
                    "total_cost": 0,
                    "message": f"エラー: 経路{i+1}に必須キーが不足しています: {missing_keys}"
                }

        
        #合計交通費の計算
        total_cost = sum(float(route.get("cost", 0)) for route in routes)
        
        #ファイル名の生成
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"交通費申請書_{timestamp}.xlsx"
        
        #出力ディレクトリの設定
        output_path = Path("output")
        output_path.mkdir(parents=True, exist_ok=True)
        
        #ファイルパスの生成
        file_path = output_path / filename
        
        #申請日の取得
        report_date = datetime.now().strftime("%Y-%m-%d")
        
        #Excelワークブック作成
        wb = Workbook()
        ws = wb.active
        ws.title = "交通費申請書"
        
        #スタイル定義
        header_font = Font(bold=True, size=12)
        header_fill = PatternFill(start_color="CCE5FF", end_color="CCE5FF", fill_type="solid")
        header_alignment = Alignment(horizontal="center", vertical="center")
        
        title_font = Font(bold=True, size=14)
        title_alignment = Alignment(horizontal="center", vertical="center")
        
        label_font = Font(bold=True, size=12)
        label_fill = PatternFill(start_color="CCE5FF", end_color="CCE5FF", fill_type="solid")
        
        total_font = Font(bold=True, size=12)
        total_alignment = Alignment(horizontal="right", vertical="center")
        
        data_alignment_center = Alignment(horizontal="center", vertical="center")
        data_alignment_right = Alignment(horizontal="right", vertical="center")
        
        #タイトル行の作成
        ws["A1"] = "交通費申請書"
        ws["A1"].font = title_font
        ws["A1"].alignment = title_alignment
        ws.merge_cells("A1:F1")
        
        #申請者情報の作成
        current_row = 3
        
        #申請者ID
        ws[f"A{current_row}"] = "申請者ID"
        ws[f"A{current_row}"].font = label_font
        ws[f"A{current_row}"].fill = label_fill
        ws[f"B{current_row}"] = user_id
        current_row += 1
        
        #申請日
        ws[f"A{current_row}"] = "申請日"
        ws[f"A{current_row}"].font = label_font
        ws[f"A{current_row}"].fill = label_fill
        ws[f"B{current_row}"] = report_date
        current_row += 1
        
        # 空行
        current_row += 1
        
        #テーブルヘッダーの作成
        header_row = current_row
        headers = ["No", "日付", "出発地", "目的地", "交通手段", "費用"]
        columns = ["A", "B", "C", "D", "E", "F"]
        
        for col, header_text in zip(columns, headers):
            cell = ws[f"{col}{header_row}"]
            cell.value = header_text
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment
        
        current_row += 1
        
        #データ行の作成
        transport_map = {
            "train": "電車",
            "bus": "バス",
            "taxi": "タクシー",
            "airplane": "飛行機"
        }
        
        for i, route in enumerate(routes, start=1):
            # No列（A列）
            ws[f"A{current_row}"] = i
            ws[f"A{current_row}"].alignment = data_alignment_center
            
            # 日付列（B列）
            ws[f"B{current_row}"] = route.get("date", "")
            ws[f"B{current_row}"].alignment = data_alignment_center
            
            # 出発地列（C列）
            ws[f"C{current_row}"] = route["departure"]
            ws[f"C{current_row}"].alignment = data_alignment_center
            
            # 目的地列（D列）
            ws[f"D{current_row}"] = route["destination"]
            ws[f"D{current_row}"].alignment = data_alignment_center
            
            # 交通手段列（E列）
            transport_type = route["transport_type"]
            transport_name = transport_map.get(transport_type, transport_type)
            ws[f"E{current_row}"] = transport_name
            ws[f"E{current_row}"].alignment = data_alignment_center
            
            # 費用列（F列）
            ws[f"F{current_row}"] = f"¥{route['cost']:,.0f}"
            ws[f"F{current_row}"].alignment = data_alignment_right
            
            current_row += 1
        
        #合計行の作成
        current_row += 1
        
        ws[f"E{current_row}"] = "合計交通費"
        ws[f"E{current_row}"].font = total_font
        ws[f"E{current_row}"].alignment = total_alignment
        
        ws[f"F{current_row}"] = f"¥{total_cost:,.0f}"
        ws[f"F{current_row}"].font = total_font
        ws[f"F{current_row}"].alignment = total_alignment
        
        #列幅調整とファイル保存
        ws.column_dimensions["A"].width = 5
        ws.column_dimensions["B"].width = 12
        ws.column_dimensions["C"].width = 15
        ws.column_dimensions["D"].width = 15
        ws.column_dimensions["E"].width = 12
        ws.column_dimensions["F"].width = 15
        
        wb.save(file_path)
        
        #戻り値の設定
        return {
            "success": True,
            "file_path": str(file_path),
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










