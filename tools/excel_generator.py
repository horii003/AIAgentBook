"""
Excel生成ツール

領収書データからExcel形式の経費精算申請書を生成します。
"""

from typing import List
from datetime import datetime
from pathlib import Path
from strands import tool
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from handlers.approval_rules import ApprovalRuleEngine


@tool
def excel_generator(
    applicant_name: str,
    store_name: str,
    amount: float,
    date: str,
    items: List[str],
    expense_category: str,
    output_directory: str
) -> str:
    """
    Excel形式の経費精算申請書を生成する。
    
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
        output_directory: 出力ディレクトリのパス
        
    Returns:
        str: 生成されたExcelファイルのパス、またはエラーメッセージ
        
    Raises:
        ValueError: 金額が30,000円を超える場合
    """
    # 金額チェック
    approved, message = ApprovalRuleEngine.check_amount(amount)
    if not approved:
        raise ValueError(message)
    
    # 出力ディレクトリの作成
    output_path = Path(output_directory)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # ファイル名の生成（タイムスタンプ付き）
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"経費精算申請書_{timestamp}.xlsx"
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
    
    return str(file_path)
