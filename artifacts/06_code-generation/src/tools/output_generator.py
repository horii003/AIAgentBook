"""申請書生成ツール（Excel出力）

経費精算申請書・交通費精算申請書をExcelテンプレートから生成する。
"""

import logging
import os
from datetime import datetime
from pathlib import Path

from openpyxl import load_workbook
from pydantic import ValidationError
from strands import ToolContext, tool

from handlers.error_handler import ErrorHandler
from models.data_models import ExpenseReportInput, ReportOutput, TransportReportInput

_logger = logging.getLogger(__name__)

_TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "template"
_OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"

_EXPENSE_TEMPLATE = _TEMPLATE_DIR / "経費精算申請書テンプレート.xlsx"
_TRANSPORT_TEMPLATE = _TEMPLATE_DIR / "交通費精算申請書テンプレート.xlsx"


def _generate_form(
    template_path: Path,
    applicant_name: str,
    application_date: str,
    write_detail_rows,
    validated,
    output_prefix: str,
) -> dict:
    """共通フォーム生成処理（テンプレート読み込み→書き込み→保存）"""
    if not template_path.exists():
        return {
            "success": False,
            "file_path": None,
            "error_message": "テンプレートファイルが見つかりません。担当者にお問い合わせください。",
        }

    try:
        _OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        wb = load_workbook(str(template_path))
        ws = wb.active

        # ヘッダー情報書き込み
        ws["B3"] = applicant_name
        ws["B4"] = application_date

        # 明細行書き込み
        write_detail_rows(ws, validated)

        # ファイル保存
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{output_prefix}_{timestamp}.xlsx"
        output_path = _OUTPUT_DIR / filename
        wb.save(str(output_path))
        wb.close()

        _logger.info("申請書生成完了: %s", filename)
        return {"success": True, "file_path": str(output_path), "error_message": None}
    except Exception as e:
        _logger.error("ファイル保存エラー: %s", e, exc_info=True)
        return {
            "success": False,
            "file_path": None,
            "error_message": ErrorHandler.handle_file_save_error(e),
        }


def _write_expense_detail_rows(ws, validated: ExpenseReportInput) -> None:
    """経費明細行を書き込む"""
    start_row = 7
    total = 0
    for i, item in enumerate(validated.items):
        row = start_row + i
        ws.cell(row=row, column=1, value=item.purchase_date)
        ws.cell(row=row, column=2, value=item.store_name)
        ws.cell(row=row, column=3, value=item.item_name)
        ws.cell(row=row, column=4, value=item.expense_category)
        ws.cell(row=row, column=5, value=item.amount)
        ws.cell(row=row, column=6, value=item.business_purpose)
        total += item.amount
    # 合計値をH9に書き込む（G9のラベルはテンプレートに既存）
    ws["H9"] = total


def _write_transport_detail_rows(ws, validated: TransportReportInput) -> None:
    """移動明細行を書き込む"""
    start_row = 7
    total = 0
    for i, item in enumerate(validated.items):
        row = start_row + i
        ws.cell(row=row, column=1, value=item.travel_date)
        ws.cell(row=row, column=2, value=item.departure)
        ws.cell(row=row, column=3, value=item.destination)
        ws.cell(row=row, column=4, value=item.transport_type)
        ws.cell(row=row, column=5, value=item.fare)
        ws.cell(row=row, column=6, value=item.business_purpose)
        total += item.fare
    # 合計値をH9に書き込む（G9のラベルはテンプレートに既存）
    ws["H9"] = total


@tool(context=True)
def generate_expense_report(items: list, tool_context: ToolContext) -> dict:
    """経費精算申請書を生成する。

    Args:
        items: 経費明細のリスト。各要素は以下のフィールドを持つ辞書:
            - purchase_date (str): 購入日（YYYY-MM-DD）【必須】
            - store_name (str): 店舗名【必須】
            - item_name (str): 品目【必須】
            - expense_category (str): 経費区分（事務用品費/宿泊費/資格精算費/その他経費）【必須】
            - amount (int): 金額（円）【必須】
            - business_purpose (str): 業務目的【必須】
    """
    applicant_name = tool_context.invocation_state.get("applicant_name", "")
    application_date = tool_context.invocation_state.get("application_date", "")

    try:
        validated = ExpenseReportInput(items=items)
    except ValidationError as e:
        _logger.error("バリデーションエラー: %s", e, exc_info=True)
        return {
            "success": False,
            "file_path": None,
            "error_message": ErrorHandler.handle_validation_error(e),
        }

    return _generate_form(
        template_path=_EXPENSE_TEMPLATE,
        applicant_name=applicant_name,
        application_date=application_date,
        write_detail_rows=_write_expense_detail_rows,
        validated=validated,
        output_prefix="経費精算申請書",
    )


@tool(context=True)
def generate_transport_report(items: list, tool_context: ToolContext) -> dict:
    """交通費精算申請書を生成する。

    Args:
        items: 移動明細のリスト。各要素は以下のフィールドを持つ辞書:
            - travel_date (str): 移動日（YYYY-MM-DD）【必須】
            - departure (str): 出発地【必須】
            - destination (str): 目的地【必須】
            - transport_type (str): 交通手段（電車/バス/タクシー/飛行機）【必須】
            - fare (int): 費用（円）【必須】
            - business_purpose (str): 業務目的【必須】
    """
    applicant_name = tool_context.invocation_state.get("applicant_name", "")
    application_date = tool_context.invocation_state.get("application_date", "")

    try:
        validated = TransportReportInput(items=items)
    except ValidationError as e:
        _logger.error("バリデーションエラー: %s", e, exc_info=True)
        return {
            "success": False,
            "file_path": None,
            "error_message": ErrorHandler.handle_validation_error(e),
        }

    return _generate_form(
        template_path=_TRANSPORT_TEMPLATE,
        applicant_name=applicant_name,
        application_date=application_date,
        write_detail_rows=_write_transport_detail_rows,
        validated=validated,
        output_prefix="交通費精算申請書",
    )
