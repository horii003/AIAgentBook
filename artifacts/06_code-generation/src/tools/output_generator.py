"""申請書生成ツール。

収集済み情報（申請者名・移動情報または経費情報・上長承認要否フラグ等）を
申請書テンプレートに反映し、Excelファイルを生成する。
申請者名・申請日は invocation_state から取得する。
"""
import logging
import os
from datetime import datetime
from typing import Literal, List, Optional

import openpyxl
from pydantic import BaseModel, Field, ValidationError, field_validator
from strands import tool
from strands import ToolContext

from handlers.error_handler import ErrorHandler
from models.data_models import (
    normalize_expense_category,
    normalize_transport_type,
    validate_date_format,
)

_logger = logging.getLogger(__name__)

# テンプレートファイルパス
_TRANSPORT_TEMPLATE_PATH = "template/交通費精算申請書テンプレート.xlsx"
_GENERAL_EXPENSE_TEMPLATE_PATH = "template/経費精算申請書テンプレート.xlsx"

# 出力先ディレクトリ
_OUTPUT_DIR = "output"


# ============ データモデル ============

class TransportRecord(BaseModel):
    """移動区間1件の情報。"""

    travel_date: str = Field(..., description="移動日（YYYY-MM-DD形式）")
    departure: str = Field(..., min_length=1, description="出発地")
    destination: str = Field(..., min_length=1, description="目的地")
    transport_type: Literal["電車", "バス", "タクシー", "飛行機"] = Field(
        ..., description="交通手段"
    )
    fare: int = Field(..., ge=0, description="運賃（円）")
    business_purpose: str = Field(..., min_length=1, description="業務目的")

    _validate_travel_date = field_validator("travel_date", mode="before")(
        classmethod(validate_date_format)
    )
    _validate_transport_type = field_validator("transport_type", mode="before")(
        classmethod(normalize_transport_type)
    )


class TransportExpenseFormInput(BaseModel):
    """generate_transport_expense_form ツールの入力バリデーション。"""

    transport_records: List[TransportRecord] = Field(
        ..., min_length=1, description="移動区間リスト"
    )
    needs_approval: bool = Field(..., description="上長承認要否フラグ")


class ExpenseRecord(BaseModel):
    """経費1件の情報。"""

    expense_date: str = Field(..., description="購入日（YYYY-MM-DD形式）")
    store_name: str = Field(..., min_length=1, description="店舗名")
    item_name: str = Field(..., min_length=1, description="品目")
    amount: int = Field(..., ge=0, description="金額（円）")
    category: Literal["事務用品費", "宿泊費", "資格精算費", "その他経費"] = Field(
        ..., description="経費区分"
    )
    business_purpose: str = Field(..., min_length=1, description="業務目的")

    _validate_expense_date = field_validator("expense_date", mode="before")(
        classmethod(validate_date_format)
    )
    _validate_category = field_validator("category", mode="before")(
        classmethod(normalize_expense_category)
    )


class GeneralExpenseFormInput(BaseModel):
    """generate_general_expense_form ツールの入力バリデーション。"""

    expense_records: List[ExpenseRecord] = Field(
        ..., min_length=1, description="経費情報リスト"
    )
    needs_approval: bool = Field(..., description="上長承認要否フラグ")


class FormGeneratorOutput(BaseModel):
    """申請書生成ツールの出力スキーマ。"""

    success: bool = Field(..., description="生成成否フラグ")
    file_path: Optional[str] = Field(None, description="生成済み申請書ファイルパス")
    error_message: Optional[str] = Field(None, description="エラーメッセージ")


# ============ 補助関数 ============

def _save_form(wb, file_path: str) -> tuple:
    """ワークブックをファイルに保存する。

    Args:
        wb: openpyxl ワークブック
        file_path: 保存先ファイルパス

    Returns:
        tuple: (True, "") 成功時、(False, エラーメッセージ) 失敗時
    """
    try:
        wb.save(file_path)
        return (True, "")
    except Exception as e:
        _logger.error("ファイル保存エラー: %s", file_path, exc_info=True)
        return (False, ErrorHandler.handle_file_save_error(e))


def _write_transport_rows(ws, validated: TransportExpenseFormInput) -> None:
    """交通費精算申請書の移動区間明細行を書き込む。

    Args:
        ws: openpyxl ワークシート
        validated: バリデーション済み入力データ
    """
    start_row = 7  # 明細開始行（テンプレートに依存: 行6がヘッダー）
    for i, record in enumerate(validated.transport_records):
        row = start_row + i
        ws.cell(row=row, column=1, value=i + 1)  # No
        ws.cell(row=row, column=2, value=record.travel_date)  # 移動日
        ws.cell(row=row, column=3, value=record.departure)  # 出発地
        ws.cell(row=row, column=4, value=record.destination)  # 目的地
        ws.cell(row=row, column=5, value=record.transport_type)  # 交通手段
        ws.cell(row=row, column=6, value=record.fare)  # 費用
        ws.cell(row=row, column=7, value=record.business_purpose)  # 業務目的
        ws.cell(row=row, column=8, value="")  # 承認状況


def _write_expense_rows(ws, validated: GeneralExpenseFormInput) -> None:
    """経費精算申請書の経費明細行を書き込む。

    Args:
        ws: openpyxl ワークシート
        validated: バリデーション済み入力データ
    """
    start_row = 7  # 明細開始行（テンプレートに依存: 行6がヘッダー）
    for i, record in enumerate(validated.expense_records):
        row = start_row + i
        ws.cell(row=row, column=1, value=i + 1)  # No
        ws.cell(row=row, column=2, value=record.expense_date)  # 購入日
        ws.cell(row=row, column=3, value=record.store_name)  # 店舗名
        ws.cell(row=row, column=4, value=record.item_name)  # 品目
        ws.cell(row=row, column=5, value=record.category)  # 経費区分
        ws.cell(row=row, column=6, value=record.amount)  # 金額
        ws.cell(row=row, column=7, value=record.business_purpose)  # 業務目的
        ws.cell(row=row, column=8, value="")  # 承認状況


def _generate_form(
    template_path: str,
    validated,
    write_detail_rows,
    output_prefix: str,
    user_name: str,
    request_date: str,
) -> tuple:
    """テンプレート読み込み・セル書き込み・ファイル保存の共通処理。

    Args:
        template_path: テンプレートファイルパス
        validated: バリデーション済み入力データ
        write_detail_rows: 明細行書き込み関数
        output_prefix: 出力ファイル名プレフィックス
        user_name: 申請者名
        request_date: 申請日

    Returns:
        tuple: (True, file_path) 成功時、(False, エラーメッセージ) 失敗時
    """
    # テンプレートファイル存在確認
    if not os.path.exists(template_path):
        _logger.warning("テンプレートファイルが見つかりません: %s", template_path)
        return (False, ErrorHandler.handle_file_save_error(FileNotFoundError(template_path)))

    # テンプレート読み込み
    wb = openpyxl.load_workbook(template_path)
    ws = wb.active

    # ヘッダーセルに申請者名・申請日を書き込む（テンプレート: A3=申請者名ラベル, B3=値）
    ws["B3"] = user_name
    ws["B4"] = request_date

    # 上長承認欄の追加
    if validated.needs_approval:
        # 承認欄を追加（テンプレートに依存）
        ws["B5"] = "上長承認要"

    # 明細行を書き込む
    write_detail_rows(ws, validated)

    # 出力ファイルパスを生成
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"{output_prefix}_{timestamp}.xlsx"
    file_path = os.path.join(_OUTPUT_DIR, output_filename)
    os.makedirs(_OUTPUT_DIR, exist_ok=True)

    # ファイル保存
    ok, err_msg = _save_form(wb, file_path)
    if not ok:
        return (False, err_msg)

    return (True, file_path)


# ============ ツール関数 ============

@tool(context=True)
def generate_transport_expense_form(
    transport_records: list,
    needs_approval: bool,
    tool_context: ToolContext,
) -> dict:
    """交通費精算申請書（Excel）を生成する。
    申請者名・申請日は invocation_state から取得する。

    Args:
        transport_records: 移動区間情報のリスト。各要素は以下のキーを持つ辞書:
            - travel_date (str): 移動日（YYYY-MM-DD形式）【必須】
            - departure (str): 出発地【必須】
            - destination (str): 目的地【必須】
            - transport_type (str): 交通手段（電車・バス・タクシー・飛行機）【必須】
            - fare (int): 運賃（円、0以上）【必須】
            - business_purpose (str): 業務目的【必須】
        needs_approval: 上長承認要否フラグ【必須】

    Returns:
        dict: 以下のキーを持つ辞書:
            - success (bool): 生成成否フラグ
            - file_path (str | None): 生成済み申請書ファイルパス。正常時のみ設定。
            - error_message (str | None): エラーメッセージ。エラー時のみ設定。
    """
    # invocation_state から申請者名・申請日を取得
    user_name = tool_context.invocation_state.get("user_name", "")
    request_date = tool_context.invocation_state.get("request_date", "")

    _logger.info("交通費精算申請書生成開始: user_name=%s", user_name)

    # 入力バリデーション
    try:
        validated = TransportExpenseFormInput(
            transport_records=transport_records,
            needs_approval=needs_approval,
        )
    except ValidationError as e:
        _logger.error("バリデーションエラー（交通費申請書）: %s", e, exc_info=True)
        return {
            "success": False,
            "file_path": None,
            "error_message": ErrorHandler.handle_validation_error(e),
        }

    # 申請書生成
    ok, result = _generate_form(
        template_path=_TRANSPORT_TEMPLATE_PATH,
        validated=validated,
        write_detail_rows=_write_transport_rows,
        output_prefix="交通費精算申請書",
        user_name=user_name,
        request_date=request_date,
    )

    if ok:
        _logger.info("交通費精算申請書生成成功: file_path=%s", result)
        return {"success": True, "file_path": result, "error_message": None}
    else:
        return {"success": False, "file_path": None, "error_message": result}


@tool(context=True)
def generate_general_expense_form(
    expense_records: list,
    needs_approval: bool,
    tool_context: ToolContext,
) -> dict:
    """経費精算申請書（Excel）を生成する。
    申請者名・申請日は invocation_state から取得する。

    Args:
        expense_records: 経費情報のリスト。各要素は以下のキーを持つ辞書:
            - expense_date (str): 購入日（YYYY-MM-DD形式）【必須】
            - store_name (str): 店舗名【必須】
            - item_name (str): 品目【必須】
            - amount (int): 金額（円、0以上）【必須】
            - category (str): 経費区分（事務用品費・宿泊費・資格精算費・その他経費）【必須】
            - business_purpose (str): 業務目的【必須】
        needs_approval: 上長承認要否フラグ【必須】

    Returns:
        dict: 以下のキーを持つ辞書:
            - success (bool): 生成成否フラグ
            - file_path (str | None): 生成済み申請書ファイルパス。正常時のみ設定。
            - error_message (str | None): エラーメッセージ。エラー時のみ設定。
    """
    # invocation_state から申請者名・申請日を取得
    user_name = tool_context.invocation_state.get("user_name", "")
    request_date = tool_context.invocation_state.get("request_date", "")

    _logger.info("経費精算申請書生成開始: user_name=%s", user_name)

    # 入力バリデーション
    try:
        validated = GeneralExpenseFormInput(
            expense_records=expense_records,
            needs_approval=needs_approval,
        )
    except ValidationError as e:
        _logger.error("バリデーションエラー（経費申請書）: %s", e, exc_info=True)
        return {
            "success": False,
            "file_path": None,
            "error_message": ErrorHandler.handle_validation_error(e),
        }

    # 申請書生成
    ok, result = _generate_form(
        template_path=_GENERAL_EXPENSE_TEMPLATE_PATH,
        validated=validated,
        write_detail_rows=_write_expense_rows,
        output_prefix="経費精算申請書",
        user_name=user_name,
        request_date=request_date,
    )

    if ok:
        _logger.info("経費精算申請書生成成功: file_path=%s", result)
        return {"success": True, "file_path": result, "error_message": None}
    else:
        return {"success": False, "file_path": None, "error_message": result}
