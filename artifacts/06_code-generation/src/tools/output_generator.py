"""申請書生成ツール

収集した申請情報をExcelテンプレートに書き込み、申請書ファイルを生成するツール関数を提供する。
"""
import logging
import os
from datetime import datetime
from pydantic import ValidationError
from strands import tool, ToolContext
import openpyxl
from models.data_models import (
    TransportFormInput,
    TransportItem,
    ExpenseFormInput,
    ExpenseItem,
)
from handlers.error_handler import ErrorHandler

_logger = logging.getLogger(__name__)

# テンプレートファイルパス
_TRANSPORT_TEMPLATE_PATH = "template/交通費精算申請書_template.xlsx"
_EXPENSE_TEMPLATE_PATH = "template/経費精算申請書_template.xlsx"

# 出力ディレクトリ
_OUTPUT_DIR = "output"


def _write_transport_rows(ws, items: list[TransportItem], start_row: int) -> None:
    """交通費精算申請書の移動明細行をExcelシートに書き込む

    Args:
        ws: openpyxlのワークシートオブジェクト
        items: 移動明細リスト
        start_row: 書き込み開始行番号
    """
    for i, item in enumerate(items):
        row = start_row + i
        ws.cell(row=row, column=1, value=i + 1)          # A: No
        ws.cell(row=row, column=2, value=item.travel_date)    # B: 移動日
        ws.cell(row=row, column=3, value=item.departure)      # C: 出発地
        ws.cell(row=row, column=4, value=item.destination)    # D: 目的地
        ws.cell(row=row, column=5, value=item.transport_type) # E: 交通手段
        ws.cell(row=row, column=6, value=item.fare)           # F: 費用
        ws.cell(row=row, column=7, value=item.purpose)        # G: 業務目的
        ws.cell(row=row, column=8, value="")                  # H: 承認状況


def _write_expense_rows(ws, items: list[ExpenseItem], start_row: int) -> None:
    """経費精算申請書の経費明細行をExcelシートに書き込む

    Args:
        ws: openpyxlのワークシートオブジェクト
        items: 経費明細リスト
        start_row: 書き込み開始行番号
    """
    for i, item in enumerate(items):
        row = start_row + i
        ws.cell(row=row, column=1, value=i + 1)              # A: No
        ws.cell(row=row, column=2, value=item.purchase_date)  # B: 購入日
        ws.cell(row=row, column=3, value="")                  # C: 店舗名（空欄）
        ws.cell(row=row, column=4, value=item.item_name)      # D: 品目
        ws.cell(row=row, column=5, value=item.expense_category) # E: 経費区分
        ws.cell(row=row, column=6, value=item.amount)         # F: 金額
        ws.cell(row=row, column=7, value=item.purpose)        # G: 業務目的
        ws.cell(row=row, column=8, value="")                  # H: 承認状況


def _save_workbook(workbook, file_path: str) -> tuple[bool, str]:
    """Excelワークブックをファイルに保存する

    Args:
        workbook: openpyxlのワークブックオブジェクト
        file_path: 保存先ファイルパス

    Returns:
        tuple[bool, str]: (成功フラグ, エラーメッセージ)
    """
    try:
        workbook.save(file_path)
        return (True, "")
    except Exception as e:
        _logger.error("申請書の保存中にエラーが発生しました: %s", file_path, exc_info=True)
        return (False, ErrorHandler.handle_file_save_error(e))


def _generate_form(
    template_path: str,
    validated,
    write_rows_fn,
    output_filename: str,
) -> dict:
    """共通フォーム生成処理（テンプレート読み込み → 書き込み → 保存）

    Args:
        template_path: テンプレートファイルパス
        validated: バリデーション済みの入力モデル
        write_rows_fn: 明細行書き込み関数
        output_filename: 出力ファイル名（拡張子なし）

    Returns:
        dict: 処理結果辞書
    """
    _empty = {"success": False, "file_path": "", "error_message": ""}

    # テンプレートファイル存在確認
    if not os.path.exists(template_path):
        _logger.error("テンプレートファイルが見つかりません: %s", template_path, exc_info=True)
        return {**_empty, "error_message": f"テンプレートファイルが見つかりません: {template_path}"}

    # 出力ファイルパス生成
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs(_OUTPUT_DIR, exist_ok=True)
    file_path = os.path.join(_OUTPUT_DIR, f"{output_filename}_{timestamp}.xlsx")

    # Excelテンプレート読み込み・書き込み
    wb = openpyxl.load_workbook(template_path)
    ws = wb.active
    # ヘッダー情報書き込み（B3=申請者名、B4=申請日）
    ws["B3"] = validated.applicant_name
    ws["B4"] = validated.application_date
    # 明細行書き込み（7行目から）
    write_rows_fn(ws, validated.items, 7)
    # 合計金額書き込み（H9）
    total = sum(getattr(item, "fare", None) or getattr(item, "amount", 0) for item in validated.items)
    ws["H9"] = total

    # ファイル保存
    ok, err = _save_workbook(wb, file_path)
    if not ok:
        return {**_empty, "error_message": err}

    return {"success": True, "file_path": file_path, "error_message": ""}


@tool(context=True)
def generate_transport_form(items: list, tool_context: ToolContext) -> dict:
    """交通費精算申請書（Excel）を生成してoutput/ディレクトリに保存する。

    HumanApprovalHookによりユーザーのOK選択後のみ実行される。
    申請者名・申請日はinvocation_stateから取得する。
    出力ファイルパスはツール内部でタイムスタンプをもとに自律生成する。

    Args:
        items: 移動明細リスト（min_length=1）。各要素は以下のキーを持つ辞書:
            - travel_date (str): 移動日（YYYY-MM-DD形式）【必須】
            - departure (str): 出発地【必須】
            - destination (str): 目的地【必須】
            - transport_type (str): 交通手段（電車・バス・タクシー・飛行機）【必須】
            - fare (float): 交通費（円、0以上）【必須】
            - purpose (str): 業務目的（空文字禁止）【必須】

    Returns:
        dict: 以下のキーを持つ辞書:
            - success (bool): 処理成功フラグ
            - file_path (str): 生成ファイルパス
            - error_message (str): エラーメッセージ
    """
    _empty = {"success": False, "file_path": "", "error_message": ""}
    applicant_name = tool_context.invocation_state.get("applicant_name", "")
    application_date = tool_context.invocation_state.get("application_date", "")
    _logger.info("交通費精算申請書の生成を開始します: 申請者=%s", applicant_name)

    try:
        validated = TransportFormInput(
            applicant_name=applicant_name,
            application_date=application_date,
            items=items,
        )
    except ValidationError as e:
        _logger.error("バリデーションエラーが発生しました", exc_info=True)
        return {**_empty, "error_message": ErrorHandler.handle_validation_error(e)}

    try:
        result = _generate_form(
            template_path=_TRANSPORT_TEMPLATE_PATH,
            validated=validated,
            write_rows_fn=_write_transport_rows,
            output_filename="交通費精算申請書",
        )
        if result["success"]:
            _logger.info("交通費精算申請書を生成しました: %s", result["file_path"])
        return result
    except Exception as e:
        _logger.error("申請書生成中に予期しないエラーが発生しました", exc_info=True)
        return {**_empty, "error_message": ErrorHandler.handle_unexpected_error(e)}


@tool(context=True)
def generate_expense_form(items: list, tool_context: ToolContext) -> dict:
    """経費精算申請書（Excel）を生成してoutput/ディレクトリに保存する。

    HumanApprovalHookによりユーザーのOK選択後のみ実行される。
    申請者名・申請日はinvocation_stateから取得する。
    出力ファイルパスはツール内部でタイムスタンプをもとに自律生成する。

    Args:
        items: 経費明細リスト（min_length=1）。各要素は以下のキーを持つ辞書:
            - purchase_date (str): 購入日（YYYY-MM-DD形式）【必須】
            - item_name (str): 品目（空文字禁止）【必須】
            - amount (float): 金額（円、0以上）【必須】
            - expense_category (str): 経費区分（事務用品費・宿泊費・資格精算費・その他経費）【必須】
            - purpose (str): 業務目的（空文字禁止）【必須】

    Returns:
        dict: 以下のキーを持つ辞書:
            - success (bool): 処理成功フラグ
            - file_path (str): 生成ファイルパス
            - error_message (str): エラーメッセージ
    """
    _empty = {"success": False, "file_path": "", "error_message": ""}
    applicant_name = tool_context.invocation_state.get("applicant_name", "")
    application_date = tool_context.invocation_state.get("application_date", "")
    _logger.info("経費精算申請書の生成を開始します: 申請者=%s", applicant_name)

    try:
        validated = ExpenseFormInput(
            applicant_name=applicant_name,
            application_date=application_date,
            items=items,
        )
    except ValidationError as e:
        _logger.error("バリデーションエラーが発生しました", exc_info=True)
        return {**_empty, "error_message": ErrorHandler.handle_validation_error(e)}

    try:
        result = _generate_form(
            template_path=_EXPENSE_TEMPLATE_PATH,
            validated=validated,
            write_rows_fn=_write_expense_rows,
            output_filename="経費精算申請書",
        )
        if result["success"]:
            _logger.info("経費精算申請書を生成しました: %s", result["file_path"])
        return result
    except Exception as e:
        _logger.error("申請書生成中に予期しないエラーが発生しました", exc_info=True)
        return {**_empty, "error_message": ErrorHandler.handle_unexpected_error(e)}
