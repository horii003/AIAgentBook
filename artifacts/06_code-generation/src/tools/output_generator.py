"""申請書生成ツール

収集した申請情報を申請書テンプレート（Excel）に入力し、申請書ファイルを生成・保存する。
"""
import logging
import os
from datetime import datetime
from pydantic import ValidationError
from strands import tool, ToolContext
from openpyxl import load_workbook
from models.data_models import ExpenseReportInput, TransportReportInput
from handlers.error_handler import ErrorHandler

_logger = logging.getLogger(__name__)

_EXPENSE_TEMPLATE_PATH = "template/経費精算申請書テンプレート.xlsx"
_TRANSPORT_TEMPLATE_PATH = "template/交通費精算申請書テンプレート.xlsx"
_OUTPUT_DIR = "output"


def _write_expense_detail_rows(ws, items) -> None:
    """経費精算申請書の明細行を書き込む。

    Args:
        ws: openpyxl ワークシート
        items: ExpenseItem のリスト
    """
    for i, item in enumerate(items):
        row = 7 + i
        ws[f"A{row}"] = i + 1
        ws[f"B{row}"] = item.purchase_date
        ws[f"C{row}"] = item.store_name
        ws[f"D{row}"] = item.item_name
        ws[f"E{row}"] = item.expense_category
        ws[f"F{row}"] = item.amount
        ws[f"G{row}"] = item.business_purpose


def _write_transport_detail_rows(ws, items) -> None:
    """交通費精算申請書の明細行を書き込む。

    Args:
        ws: openpyxl ワークシート
        items: TransportItem のリスト
    """
    for i, item in enumerate(items):
        row = 7 + i
        ws[f"A{row}"] = i + 1
        ws[f"B{row}"] = item.travel_date
        ws[f"C{row}"] = item.departure
        ws[f"D{row}"] = item.destination
        ws[f"E{row}"] = item.transport_type
        ws[f"F{row}"] = item.fare
        ws[f"G{row}"] = item.business_purpose


def _generate_form(
    template_path: str,
    validated,
    applicant_name: str,
    application_date: str,
    write_detail_rows,
    output_filename: str,
) -> tuple:
    """共通フォーム生成処理（テンプレート読み込み → 書き込み → 保存）。

    Args:
        template_path: テンプレートファイルパス
        validated: バリデーション済みモデルインスタンス
        applicant_name: 申請者名
        application_date: 申請日
        write_detail_rows: 明細行書き込み関数
        output_filename: 出力ファイル名（拡張子なし）

    Returns:
        tuple[bool, str]: (成功フラグ, ファイルパスまたはエラーメッセージ)
    """
    if not os.path.exists(template_path):
        _logger.error("テンプレートファイルが見つかりません: file_path=%s", template_path)
        return (False, "申請書テンプレートが見つかりませんでした。担当者にお問い合わせください。")

    os.makedirs(_OUTPUT_DIR, exist_ok=True)
    file_path = os.path.join(_OUTPUT_DIR, f"{output_filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")

    try:
        wb = load_workbook(template_path)
        ws = wb.active

        # ヘッダー情報書き込み
        ws["B3"] = applicant_name
        ws["B4"] = application_date

        # 明細行書き込み
        write_detail_rows(ws, validated.items)

        # 合計金額計算・書き込み
        n = len(validated.items)
        total = sum(
            getattr(item, "amount", None) or getattr(item, "fare", 0)
            for item in validated.items
        )
        ws[f"H{7 + n + 2}"] = total

        wb.save(file_path)
        _logger.info("申請書生成成功: file_path=%s", file_path)
        return (True, file_path)

    except PermissionError as e:
        _logger.error("ファイル保存エラー（権限）: %s, file_path=%s", e, file_path, exc_info=True)
        return (False, "申請書の保存に失敗しました。ファイルへのアクセス権限がありません。担当者にお問い合わせください。")
    except Exception as e:
        _logger.error("ファイル保存エラー（想定外）: %s, file_path=%s", e, file_path, exc_info=True)
        return (False, "予期しないエラーが発生しました。担当者にお問い合わせください。")


@tool(context=True)
def generate_expense_report(items: list, tool_context: ToolContext) -> dict:
    """経費精算申請書（Excel）を生成して output/ に保存する。

    申請者名・申請日は invocation_state から自動取得する。
    HumanApprovalHook による承認（OK選択）後にのみ実行される。

    Args:
        items: 経費明細のリスト。各要素は以下のキーを持つ辞書:
            - purchase_date (str): 購入日（YYYY-MM-DD 形式）【必須】
            - store_name (str): 店舗名【必須】
            - item_name (str): 品目【必須】
            - expense_category (str): 経費区分。以下のいずれか【必須】
                "事務用品費", "宿泊費", "資格精算費", "その他経費"
            - amount (int): 金額（円、0以上）【必須】
            - business_purpose (str): 業務目的【必須】
        tool_context: ツールコンテキスト（invocation_stateを含む）

    Returns:
        dict: {
            "success": bool,
            "file_path": str | None,
            "error_message": str | None
        }
    """
    applicant_name = tool_context.invocation_state.get("applicant_name")
    application_date = tool_context.invocation_state.get("application_date")
    if not applicant_name or not application_date:
        return {"success": False, "file_path": None, "error_message": "申請者情報が取得できませんでした。担当者にお問い合わせください。"}

    _logger.info("経費精算申請書生成開始: 明細%d件", len(items) if items else 0)

    try:
        validated = ExpenseReportInput(items=items)
    except ValidationError as e:
        _logger.error("バリデーションエラー: %s, file_path=None", e, exc_info=True)
        return {"success": False, "file_path": None, "error_message": ErrorHandler.handle_validation_error(e)}

    try:
        ok, result = _generate_form(
            template_path=_EXPENSE_TEMPLATE_PATH,
            validated=validated,
            applicant_name=applicant_name,
            application_date=application_date,
            write_detail_rows=_write_expense_detail_rows,
            output_filename="経費精算申請書",
        )
        if ok:
            return {"success": True, "file_path": result, "error_message": None}
        return {"success": False, "file_path": None, "error_message": result}
    except Exception as e:
        _logger.error("経費精算申請書生成エラー: %s, file_path=None", e, exc_info=True)
        return {"success": False, "file_path": None, "error_message": ErrorHandler.handle_unexpected_error(e)}


@tool(context=True)
def generate_transport_report(items: list, tool_context: ToolContext) -> dict:
    """交通費精算申請書（Excel）を生成して output/ に保存する。

    申請者名・申請日は invocation_state から自動取得する。
    HumanApprovalHook による承認（OK選択）後にのみ実行される。

    Args:
        items: 移動明細のリスト。各要素は以下のキーを持つ辞書:
            - travel_date (str): 移動日（YYYY-MM-DD 形式）【必須】
            - departure (str): 出発地【必須】
            - destination (str): 目的地【必須】
            - transport_type (str): 交通手段。以下のいずれか【必須】
                "電車", "バス", "タクシー", "飛行機"
            - fare (int): 費用（円、0以上）【必須】
            - business_purpose (str): 業務目的【必須】
        tool_context: ツールコンテキスト（invocation_stateを含む）

    Returns:
        dict: {
            "success": bool,
            "file_path": str | None,
            "error_message": str | None
        }
    """
    applicant_name = tool_context.invocation_state.get("applicant_name")
    application_date = tool_context.invocation_state.get("application_date")
    if not applicant_name or not application_date:
        return {"success": False, "file_path": None, "error_message": "申請者情報が取得できませんでした。担当者にお問い合わせください。"}

    _logger.info("交通費精算申請書生成開始: 明細%d件", len(items) if items else 0)

    try:
        validated = TransportReportInput(items=items)
    except ValidationError as e:
        _logger.error("バリデーションエラー: %s, file_path=None", e, exc_info=True)
        return {"success": False, "file_path": None, "error_message": ErrorHandler.handle_validation_error(e)}

    try:
        ok, result = _generate_form(
            template_path=_TRANSPORT_TEMPLATE_PATH,
            validated=validated,
            applicant_name=applicant_name,
            application_date=application_date,
            write_detail_rows=_write_transport_detail_rows,
            output_filename="交通費精算申請書",
        )
        if ok:
            return {"success": True, "file_path": result, "error_message": None}
        return {"success": False, "file_path": None, "error_message": result}
    except Exception as e:
        _logger.error("交通費精算申請書生成エラー: %s, file_path=None", e, exc_info=True)
        return {"success": False, "file_path": None, "error_message": ErrorHandler.handle_unexpected_error(e)}
