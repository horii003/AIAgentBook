"""
Excel申請書生成ツール

Excel形式の経費精算申請書を生成する。
- 「経費精算申請エージェント(receipt_expense_agent)」：receipt_excel_generatorツールを利用
- 「交通費精算申請エージェント(travel_agent)」：travel_excel_generatorツールを利用

"""

import os
from typing import List, Tuple
from datetime import datetime
from pathlib import Path
from strands import tool, ToolContext
from openpyxl import Workbook
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.styles import Font, Alignment, PatternFill
from pydantic import ValidationError
from handlers.error_handler import ErrorHandler
from models.data_models import RouteInput, InvocationState


# エラーハンドラーの初期化
_error_handler = ErrorHandler()


#共通ヘルパー関数
#申請者取得
def _get_applicant_name(tool_context: ToolContext) -> str:
    """
    invocation_stateから申請者名を取得する。
    
    Args:
        tool_context: AWS Strandsのツールコンテキスト
        
    Returns:
        str: 申請者名（取得できない場合は"未設定"）
    """
    if not tool_context or not tool_context.invocation_state:
        _error_handler.log_info(
            "tool_contextまたはinvocation_stateが存在しません。デフォルト値を使用します。",
            context={"default_value": "未設定"}
        )
        return "未設定"
    
    try:
        state = InvocationState(**tool_context.invocation_state)
        _error_handler.log_info(
            f"申請者名を取得しました: {state.applicant_name}"
        )
        return state.applicant_name

    except ValidationError as e:
        _error_handler.log_error(
            "ValidationError",
            f"申請者名の取得に失敗しました: {str(e)}",
            context={"invocation_state": tool_context.invocation_state}
        )
        return "未設定"


#申請日取得
def _get_application_date(tool_context: ToolContext) -> str:
    """
    invocation_stateから申請日を取得する。
    
    Args:
        tool_context: AWS Strandsのツールコンテキスト
        
    Returns:
        str: 申請日（YYYY-MM-DD形式、取得できない場合は現在日付）
    """
    default_date = datetime.now().strftime("%Y-%m-%d")
    
    if not tool_context or not tool_context.invocation_state:
        _error_handler.log_info(
            "tool_contextまたはinvocation_stateが存在しません。現在日付を使用します。",
            context={"default_date": default_date}
        )
        return default_date
    
    try:
        state = InvocationState(**tool_context.invocation_state)
        _error_handler.log_info(
            f"申請日を取得しました: {state.application_date}"
        )
        return state.application_date

    except ValidationError as e:
        _error_handler.log_error(
            "ValidationError",
            f"申請日の取得に失敗しました: {str(e)}",
            context={"invocation_state": tool_context.invocation_state}
        )
        return default_date


#ファイル名生成
def _generate_filename(prefix: str) -> str:
    """
    タイムスタンプ付きのファイル名を生成する。
    
    Args:
        prefix: ファイル名のプレフィックス（例: "経費精算申請書", "交通費申請書"）
        
    Returns:
        str: タイムスタンプ付きファイル名（例: "経費精算申請書_20240115_143022.xlsx"）
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.xlsx"


#出力ディレクトリ取得
def _ensure_output_directory() -> Path:
    """
    出力ディレクトリを作成し、そのパスを返す。
    
    Returns:
        Path: 出力ディレクトリのパス(output/)
        
    Raises:
        OSError: ディレクトリの作成に失敗した場合
    """
    
    try:
        output_path = Path("output")
        output_path.mkdir(parents=True, exist_ok=True)
        _error_handler.log_info(
            f"出力ディレクトリを確認しました: {output_path}",
            context={"output_directory": str(output_path)}
        )

    except OSError as e:
        _error_handler.log_error(
            "DirectoryCreationError",
            f"出力ディレクトリの作成に失敗しました: {str(e)}",
            context={"output_directory": str(output_path)},
            exc_info=True
        )
        raise
    
    return output_path


#Excelワークブック作成
def _create_workbook(title: str) -> Tuple[Workbook, Worksheet]:
    """
    新しいExcelワークブックとワークシートを作成する。
    
    Args:
        title: ワークシートのタイトル
        
    Returns:
        Tuple[Workbook, Worksheet]: ワークブックとワークシートのタプル
    """
    wb = Workbook()
    ws = wb.active
    ws.title = title
    return wb, ws


def _create_style_definitions() -> dict:
    """
    Excel用の共通スタイル定義を作成する。
    
    Returns:
        dict: スタイルオブジェクトの辞書
            - header_font: ヘッダー用フォント
            - header_fill: ヘッダー用背景色
            - header_alignment: ヘッダー用配置
            - title_font: タイトル用フォント
            - title_alignment: タイトル用配置
            - label_font: ラベル用フォント
            - label_fill: ラベル用背景色
            - data_alignment_center: データ中央揃え
            - data_alignment_right: データ右揃え
            - total_font: 合計用フォント
            - total_alignment: 合計用配置
    """
    return {
        "header_font": Font(bold=True, size=12),
        "header_fill": PatternFill(start_color="CCE5FF", end_color="CCE5FF", fill_type="solid"),
        "header_alignment": Alignment(horizontal="center", vertical="center"),
        "title_font": Font(bold=True, size=14),
        "title_alignment": Alignment(horizontal="center", vertical="center"),
        "label_font": Font(bold=True, size=12),
        "label_fill": PatternFill(start_color="CCE5FF", end_color="CCE5FF", fill_type="solid"),
        "data_alignment_center": Alignment(horizontal="center", vertical="center"),
        "data_alignment_right": Alignment(horizontal="right", vertical="center"),
        "total_font": Font(bold=True, size=12),
        "total_alignment": Alignment(horizontal="right", vertical="center"),
    }


def _apply_header_style(cell, styles: dict) -> None:
    """
    セルにヘッダースタイルを適用する。
    
    Args:
        cell: openpyxlのセルオブジェクト
        styles: _create_style_definitions()で作成したスタイル辞書
    """
    cell.font = styles["header_font"]
    cell.fill = styles["header_fill"]
    cell.alignment = styles["header_alignment"]


def _apply_title_style(cell, styles: dict) -> None:
    """
    セルにタイトルスタイルを適用する。
    
    Args:
        cell: openpyxlのセルオブジェクト
        styles: _create_style_definitions()で作成したスタイル辞書
    """
    cell.font = styles["title_font"]
    cell.alignment = styles["title_alignment"]


def _save_workbook(wb: Workbook, file_path: Path) -> Tuple[bool, str]:
    """
    ワークブックをファイルに保存する。
    
    Args:
        wb: 保存するワークブック
        file_path: 保存先のファイルパス
        
    Returns:
        Tuple[bool, str]: (成功フラグ, メッセージ)
            - 成功時: (True, 成功メッセージ)
            - 失敗時: (False, ユーザー向けエラーメッセージ)
    """
    
    try:
        wb.save(file_path)
        #成功時のログ出力
        _error_handler.log_info(
            f"ファイルを正常に保存しました: {file_path}",
            context={"file_path": str(file_path)}
        )

        #引数success,messageを返す
        return True, f"申請書を正常に作成しました: {file_path}"
    
    except (IOError, PermissionError) as e:
        #失敗時はerror_handlerを利用してエラーハンドリングを行う。
        user_message = _error_handler.handle_file_save_error(
            e,
            context={"file_path": str(file_path)}
        )
        #引数success,messageを返す
        return False, user_message
    
    except Exception as e:
        # 予期しないエラーの場合
        user_message = _error_handler.handle_file_save_error(
            e,
            context={"file_path": str(file_path), "error_type": "unexpected"}
        )
        #引数success,messageを返す
        return False, user_message


#専門エージェントによるツール関数
# 経費精算申請エージェント用の申請書作成ツール
@tool(context=True)
def receipt_excel_generator(
    store_name: str,
    amount: float,
    date: str,
    items: List[str],
    expense_category: str,
    tool_context: ToolContext
) -> dict:
    """
    経費精算申請エージェントが利用します。経費精算申請書を生成します。

    
    このツールは領収書データからExcel申請書を作成します。
    金額が30,000円を超える場合はエラーを返します。
    申請者名はinvocation_stateから自動的に取得されます。
    
    生成されるExcelファイルには以下の情報が含まれます：
    - 申請者名（invocation_stateから取得）
    - 申請日（自動生成）
    - 店舗名
    - 金額
    - 購入日
    - 品目リスト
    - 経費区分
    - 承認状況
    
    ファイル名は「経費精算申請書_YYYYMMDD_HHMMSS.xlsx」の形式で生成されます。
    
    Args:
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
    # ツール呼び出しログ
    _error_handler.log_info(
        "receipt_excel_generatorツールが呼び出されました",
        context={
            "store_name": store_name,
            "amount": amount,
            "date": date,
            "expense_category": expense_category
        }
    )

    #申請書作成処理開始
    try:
        # ヘルパー関数を使用して共通処理を実行
        applicant_name = _get_applicant_name(tool_context)
        application_date = _get_application_date(tool_context)
        
        # ヘルパー関数でファイル名とパスを生成
        filename = _generate_filename("経費精算申請書")
        output_path = _ensure_output_directory()
        file_path = output_path / filename
        
        _error_handler.log_info(
            "Excel申請書の生成を開始します",
            context={"file_path": str(file_path)}
        )
        
        # ヘルパー関数でワークブックとスタイルを作成
        wb, ws = _create_workbook("経費精算申請書")
        styles = _create_style_definitions()
        
        # タイトル行
        ws["A1"] = "経費精算申請書"
        _apply_title_style(ws["A1"], styles)
        ws.merge_cells("A1:B1")
        
        # 申請情報
        current_row = 3
        
        # 申請者名
        ws[f"A{current_row}"] = "申請者名"
        _apply_header_style(ws[f"A{current_row}"], styles)
        ws[f"B{current_row}"] = applicant_name
        current_row += 1
        
        # 申請日
        ws[f"A{current_row}"] = "申請日"
        _apply_header_style(ws[f"A{current_row}"], styles)
        ws[f"B{current_row}"] = application_date
        current_row += 1
        
        # 空行
        current_row += 1
        
        # 領収書情報
        ws[f"A{current_row}"] = "店舗名"
        _apply_header_style(ws[f"A{current_row}"], styles)
        ws[f"B{current_row}"] = store_name
        current_row += 1
        
        ws[f"A{current_row}"] = "金額"
        _apply_header_style(ws[f"A{current_row}"], styles)
        ws[f"B{current_row}"] = f"¥{amount:,.0f}"
        current_row += 1
        
        ws[f"A{current_row}"] = "購入日"
        _apply_header_style(ws[f"A{current_row}"], styles)
        ws[f"B{current_row}"] = date
        current_row += 1
        
        ws[f"A{current_row}"] = "経費区分"
        _apply_header_style(ws[f"A{current_row}"], styles)
        ws[f"B{current_row}"] = expense_category
        current_row += 1
        
        # 品目リスト
        ws[f"A{current_row}"] = "品目"
        _apply_header_style(ws[f"A{current_row}"], styles)
        ws[f"B{current_row}"] = ", ".join(items)
        current_row += 1
        
        # 空行
        current_row += 1
        
        # 承認状況
        ws[f"A{current_row}"] = "承認状況"
        _apply_header_style(ws[f"A{current_row}"], styles)
        ws[f"B{current_row}"] = "承認待ち"
        ws[f"B{current_row}"].font = Font(color="008000", bold=True)
        
        # 列幅の調整
        ws.column_dimensions["A"].width = 15
        ws.column_dimensions["B"].width = 40
        
        # ヘルパー関数でファイルを保存
        success, message = _save_workbook(wb, file_path)
        if success:
            return {
                "success": True,
                "file_path": str(file_path),
                "message": message
            }
        else:
            return {
                "success": False,
                "file_path": "",
                "message": message
            }
    

    #申請書作成処理のエラー（予期しないエラー）
    except Exception as e:
        _error_handler.log_error(
            "UnexpectedError",
            f"経費精算申請書の生成中に予期しないエラーが発生しました: {str(e)}",
            context={
                "store_name": store_name,
                "amount": amount,
                "date": date
            },
            exc_info=True
        )
        return {
            "success": False,
            "file_path": "",
            "message": f"エラー: 申請書の生成に失敗しました - {str(e)}"
        }


# 交通費精算申請エージェント用の申請書作成ツール
@tool(context=True)
def travel_excel_generator(
    routes: List[dict],
    tool_context: ToolContext
) -> dict:

    """
    交通費申請書をExcel形式で生成する

    交通費精算申請エージェントが利用します
    このツールは交通費の経路データからExcel申請書を作成します
    複数の経路を一覧表形式で表示し、合計交通費を計算します
    申請者名はinvocation_stateから自動的に取得されます
    
    Args:
        routes: 経路データのリスト。各要素は以下のキーを持つ辞書:
            - departure (str): 出発地
            - destination (str): 目的地
            - date (str): 日付（YYYY-MM-DD形式）
            - transport_type (str): 交通手段 (train/bus/taxi/airplane)
            - cost (float): 費用
            - notes (str, optional): 備考
    
    Returns:
        dict: {
            "success": bool,         # 成功フラグ
            "file_path": str,        # 保存されたファイルのパス
            "total_cost": float,     # 合計交通費
            "message": str           # 結果メッセージ
        }
    """
    # ツール呼び出しログ
    _error_handler.log_info(
        "travel_excel_generatorツールが呼び出されました",
        context={"routes_count": len(routes) if routes else 0}
    )
    
    #申請書作成処理開始
    try:
        # ヘルパー関数を使用して共通処理を実行
        applicant_name = _get_applicant_name(tool_context)
        application_date = _get_application_date(tool_context)

        # Pydanticモデルでバリデーション
        if not routes:
            _error_handler.log_error(
                "EmptyDataError",
                "経路データが空です",
                context={"routes": routes}
            )
            return {
                "success": False,
                "file_path": "",
                "total_cost": 0,
                "message": "エラー: 経路データが空です"
            }
        
        # 各経路データをPydanticモデルで検証
        validated_routes = []
        for i, route in enumerate(routes):
            try:
                validated_route = RouteInput(**route)
                validated_routes.append(validated_route)

            except ValidationError as e:
                error_messages = []
                for error in e.errors():
                    field = ".".join(str(loc) for loc in error["loc"])
                    error_messages.append(f"{field}: {error['msg']}")

                # handle_validation_errorでログ出力
                _error_handler.handle_validation_error(
                    e,
                    context={"route_index": i+1, "route_data": route}
                )
                
                return {
                    "success": False,
                    "file_path": "",
                    "total_cost": 0,
                    "message": f"エラー: 経路{i+1}のデータが不正です - {', '.join(error_messages)}"
                }
        
        # 合計交通費の計算
        total_cost = sum(route.cost for route in validated_routes)
        
        _error_handler.log_info(
            f"経路データの検証が完了しました。合計交通費: ¥{total_cost:,.0f}",
            context={"routes_count": len(validated_routes), "total_cost": total_cost}
        )
        
        # ヘルパー関数でファイル名とパスを生成
        filename = _generate_filename("交通費申請書")
        output_path = _ensure_output_directory()
        file_path = output_path / filename
        
        _error_handler.log_info(
            "Excel申請書の生成を開始します",
            context={"file_path": str(file_path)}
        )
        
        # ヘルパー関数でワークブックとスタイルを作成
        wb, ws = _create_workbook("交通費申請書")
        styles = _create_style_definitions()
        
        # タイトル行の作成
        ws["A1"] = "交通費申請書"
        _apply_title_style(ws["A1"], styles)
        ws.merge_cells("A1:G1")
        
        # 申請者情報の作成
        current_row = 3
        
        # 申請者名
        ws[f"A{current_row}"] = "申請者名"
        ws[f"A{current_row}"].font = styles["label_font"]
        ws[f"A{current_row}"].fill = styles["label_fill"]
        ws[f"A{current_row}"].alignment = styles["data_alignment_center"]
        ws[f"B{current_row}"] = applicant_name
        ws[f"B{current_row}"].alignment = styles["data_alignment_center"]
        current_row += 1
        
        # 申請日
        ws[f"A{current_row}"] = "申請日"
        ws[f"A{current_row}"].font = styles["label_font"]
        ws[f"A{current_row}"].fill = styles["label_fill"]
        ws[f"A{current_row}"].alignment = styles["data_alignment_center"]
        ws[f"B{current_row}"] = application_date
        ws[f"B{current_row}"].alignment = styles["data_alignment_center"]
        current_row += 1
        
        # 空行
        current_row += 1
        
        # テーブルヘッダーの作成
        header_row = current_row
        headers = ["No", "日付", "出発地", "目的地", "交通手段", "費用", "承認状況"]
        columns = ["A", "B", "C", "D", "E", "F", "G"]
        
        for col, header_text in zip(columns, headers):
            cell = ws[f"{col}{header_row}"]
            cell.value = header_text
            _apply_header_style(cell, styles)
        
        current_row += 1
        
        # データ行の作成
        transport_map = {
            "train": "電車",
            "bus": "バス",
            "taxi": "タクシー",
            "airplane": "飛行機"
        }
        
        for i, route in enumerate(validated_routes, start=1):
            # No列（A列）- 右詰め
            ws[f"A{current_row}"] = i
            ws[f"A{current_row}"].alignment = styles["data_alignment_right"]
            
            # 日付列（B列）
            ws[f"B{current_row}"] = route.date
            ws[f"B{current_row}"].alignment = styles["data_alignment_center"]
            
            # 出発地列（C列）
            ws[f"C{current_row}"] = route.departure
            ws[f"C{current_row}"].alignment = styles["data_alignment_center"]
            
            # 目的地列（D列）
            ws[f"D{current_row}"] = route.destination
            ws[f"D{current_row}"].alignment = styles["data_alignment_center"]
            
            # 交通手段列（E列）
            transport_type = route.transport_type
            transport_name = transport_map.get(transport_type, transport_type)
            ws[f"E{current_row}"] = transport_name
            ws[f"E{current_row}"].alignment = styles["data_alignment_center"]
            
            # 費用列（F列）
            ws[f"F{current_row}"] = f"¥{route.cost:,.0f}"
            ws[f"F{current_row}"].alignment = styles["data_alignment_right"]
            
            # 承認状況列（G列）- 緑色、太字
            ws[f"G{current_row}"] = "承認待ち"
            ws[f"G{current_row}"].font = Font(color="008000", bold=True)
            ws[f"G{current_row}"].alignment = styles["data_alignment_center"]
            
            current_row += 1
        
        # 合計行の作成
        current_row += 1
        
        ws[f"E{current_row}"] = "合計交通費"
        ws[f"E{current_row}"].font = styles["total_font"]
        ws[f"E{current_row}"].alignment = styles["total_alignment"]
        
        ws[f"F{current_row}"] = f"¥{total_cost:,.0f}"
        ws[f"F{current_row}"].font = styles["total_font"]
        ws[f"F{current_row}"].alignment = styles["total_alignment"]
        
        # 列幅調整
        ws.column_dimensions["A"].width = 12
        ws.column_dimensions["B"].width = 15
        ws.column_dimensions["C"].width = 15
        ws.column_dimensions["D"].width = 15
        ws.column_dimensions["E"].width = 12
        ws.column_dimensions["F"].width = 15
        ws.column_dimensions["G"].width = 12
        
        # ヘルパー関数でファイルを保存
        success, message = _save_workbook(wb, file_path)
        if success:
            return {
                "success": True,
                "file_path": str(file_path),
                "total_cost": total_cost,
                "message": message
            }
        else:
            return {
                "success": False,
                "file_path": "",
                "total_cost": 0,
                "message": message
            }
    
    #申請書作成処理のエラー（予期しないエラー）
    except Exception as e:
        _error_handler.log_error(
            "UnexpectedError",
            f"交通費申請書の生成中に予期しないエラーが発生しました: {str(e)}",
            context={"routes_count": len(routes) if routes else 0},
            exc_info=True
        )
        return {
            "success": False,
            "file_path": "",
            "total_cost": 0,
            "message": f"エラー: 申請書の生成に失敗しました - {str(e)}"
        }

