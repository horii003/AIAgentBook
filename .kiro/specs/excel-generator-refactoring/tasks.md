# Implementation Plan: Excel Generator Refactoring

## Overview

このタスクリストは、`tools/excel_generator.py`をクラスベース設計にリファクタリングするための実装計画です。現在の約700行のコードには、2つの独立した関数（`receipt_excel_generator`と`transportation_excel_generator`）が存在し、多くの共通コードが重複しています。

リファクタリングにより、以下を実現します：
- コード重複の削減（約40%のコード削減）
- 保守性の向上（クラスベース設計）
- テスト容易性の向上（各クラスを独立してテスト可能）
- 拡張性の向上（新しい申請書タイプを追加しやすい）
- 後方互換性の維持（既存のエージェントは変更不要）

## Tasks

- [x] 1. Phase 1: ExcelStyleManagerクラスの実装
  - [x] 1.1 ExcelStyleManagerクラスの基本構造を作成
    - `tools/excel_generator.py`にExcelStyleManagerクラスを追加
    - `__init__()`メソッドを実装し、`self.styles`を初期化
    - _Requirements: 1.5, 4.2_

  - [x] 1.2 _create_style_definitions()メソッドを実装
    - 既存の`_create_style_definitions()`関数のロジックをクラスメソッドに移行
    - 全てのスタイル定義（header_font, header_fill, header_alignment, title_font, title_alignment, label_font, label_fill, data_alignment_center, data_alignment_right, total_font, total_alignment）を含む辞書を返す
    - _Requirements: 1.5, 4.2_

  - [x] 1.3 スタイル適用メソッドを実装
    - `apply_header_style(cell)`メソッドを実装
    - `apply_title_style(cell)`メソッドを実装
    - `apply_label_style(cell)`メソッドを実装（新規）
    - `apply_data_style(cell, alignment)`メソッドを実装（新規）
    - _Requirements: 1.5, 4.2_

  - [ ]* 1.4 ExcelStyleManagerのユニットテストを作成
    - スタイル定義の完全性をテスト
    - 各スタイル適用メソッドの動作をテスト
    - _Requirements: 5.1, 5.2_

  - [ ]* 1.5 ExcelStyleManagerのプロパティテストを実行
    - **Property 5: スタイル定義の完全性**
    - **Validates: Requirements 1.5**

- [x] 2. Phase 2: ExcelGeneratorBase基底クラスの実装
  - [x] 2.1 ExcelGeneratorBase抽象基底クラスの基本構造を作成
    - `tools/excel_generator.py`にExcelGeneratorBase抽象基底クラスを追加
    - `from abc import ABC, abstractmethod`をインポート
    - `__init__(tool_context)`メソッドを実装し、`self.tool_context`、`self.style_manager`、`self._error_handler`を初期化
    - `generate(**kwargs)`抽象メソッドを定義
    - _Requirements: 1.1, 4.1, 4.4_

  - [x] 2.2 申請者情報取得メソッドを実装
    - 既存の`_get_applicant_name(tool_context)`関数を`_get_applicant_name(self)`メソッドに移行
    - 既存の`_get_application_date(tool_context)`関数を`_get_application_date(self)`メソッドに移行
    - `self.tool_context`を使用してinvocation_stateから情報を取得
    - エラー時はデフォルト値を返す（"未設定"、現在日付）
    - _Requirements: 1.1, 3.1, 4.1_

  - [x] 2.3 ファイル管理メソッドを実装
    - 既存の`_generate_filename(prefix)`関数を`_generate_filename(self, prefix)`メソッドに移行
    - 既存の`_ensure_output_directory()`関数を`_ensure_output_directory(self)`メソッドに移行
    - タイムスタンプフォーマット: `{prefix}_YYYYMMDD_HHMMSS.xlsx`
    - 出力ディレクトリ: `output/`
    - _Requirements: 1.2, 1.3, 4.3_

  - [x] 2.4 ワークブック管理メソッドを実装
    - 既存の`_create_workbook(title)`関数を`_create_workbook(self, title)`メソッドに移行
    - 既存の`_save_workbook(wb, file_path)`関数を`_save_workbook(self, wb, file_path)`メソッドに移行
    - エラーハンドリングを含む
    - _Requirements: 1.4, 3.1, 3.2, 4.1_

  - [x] 2.5 バリデーションエラー整形メソッドを実装
    - `_format_validation_errors(self, e: ValidationError)`メソッドを新規作成
    - Pydanticのバリデーションエラーを日本語のエラーメッセージに整形
    - _Requirements: 3.1, 3.3, 3.4_

  - [ ]* 2.6 ExcelGeneratorBaseのユニットテストを作成
    - 各メソッドの正常系をテスト
    - エラーケース（tool_contextがNone、invocation_stateが存在しない）をテスト
    - デフォルト値の動作をテスト
    - _Requirements: 5.1, 5.2_

  - [ ]* 2.7 ExcelGeneratorBaseのプロパティテストを実行
    - **Property 1: 申請者名の正確な取得**
    - **Validates: Requirements 1.1**

  - [ ]* 2.8 ファイル名フォーマットのプロパティテストを実行
    - **Property 2: ファイル名フォーマットの一貫性**
    - **Validates: Requirements 1.2**

- [x] 3. Checkpoint - 基底クラスとスタイルマネージャーの動作確認
  - 全てのテストが合格することを確認
  - 必要に応じてユーザーに質問

- [x] 4. Phase 3: ReceiptExcelGeneratorクラスの実装
  - [x] 4.1 ReceiptExcelGeneratorクラスの基本構造を作成
    - `tools/excel_generator.py`にReceiptExcelGeneratorクラスを追加（ExcelGeneratorBaseを継承）
    - クラス定数を定義（FILE_PREFIX, SHEET_TITLE, COLUMN_WIDTH_A, COLUMN_WIDTH_B）
    - _Requirements: 2.1, 2.3, 4.4_

  - [x] 4.2 generate()メソッドを実装
    - 既存の`receipt_excel_generator()`関数の処理ロジックを移行
    - パラメータ: store_name, amount, date, items, expense_category
    - Pydanticモデル（ReceiptExpenseInput）でバリデーション
    - 基底クラスのメソッドを使用（_get_applicant_name, _get_application_date, _generate_filename, _ensure_output_directory, _create_workbook, _save_workbook）
    - ExcelStyleManagerでスタイルを適用
    - 戻り値: {"success": bool, "file_path": str, "message": str}
    - _Requirements: 2.1, 2.3, 2.4, 2.5, 3.1, 3.2, 3.3, 3.4_

  - [x] 4.3 _write_receipt_data()メソッドを実装
    - 領収書データをワークシートに書き込む
    - タイトル行、申請情報、領収書データを書き込み
    - スタイルマネージャーを使用してスタイルを適用
    - 列幅を調整
    - _Requirements: 2.1, 2.3, 4.1_

  - [ ]* 4.4 ReceiptExcelGeneratorのユニットテストを作成
    - 正常系のテスト（有効なデータでExcelが生成される）
    - バリデーションエラーのテスト（不正なデータでエラーが返される）
    - ファイル保存の確認
    - _Requirements: 5.1, 5.2, 5.3_

  - [ ]* 4.5 ReceiptExcelGeneratorのプロパティテストを実行
    - **Property 3: 出力ディレクトリへの保存**
    - **Validates: Requirements 1.3**

  - [ ]* 4.6 戻り値構造のプロパティテストを実行
    - **Property 4: 戻り値構造の完全性**
    - **Validates: Requirements 1.4**

- [x] 5. Phase 4: TransportationExcelGeneratorクラスの実装
  - [x] 5.1 TransportationExcelGeneratorクラスの基本構造を作成
    - `tools/excel_generator.py`にTransportationExcelGeneratorクラスを追加（ExcelGeneratorBaseを継承）
    - クラス定数を定義（FILE_PREFIX, SHEET_TITLE, COLUMN_WIDTHS, TRANSPORT_TYPE_MAP）
    - _Requirements: 2.2, 2.4, 4.4_

  - [x] 5.2 generate()メソッドを実装
    - 既存の`transportation_excel_generator()`関数の処理ロジックを移行
    - パラメータ: routes
    - Pydanticモデル（RouteInput）でバリデーション
    - 基底クラスのメソッドを使用
    - ExcelStyleManagerでスタイルを適用
    - 戻り値: {"success": bool, "file_path": str, "total_cost": float, "message": str}
    - _Requirements: 2.2, 2.4, 2.5, 3.1, 3.2, 3.3, 3.4_

  - [x] 5.3 _calculate_total_cost()メソッドを実装
    - 経路データリストから合計交通費を計算
    - _Requirements: 2.2, 2.4_

  - [x] 5.4 _write_routes_table()メソッドを実装
    - 経路テーブルをワークシートに書き込む
    - ヘッダー行、各経路データ、合計行を書き込み
    - スタイルマネージャーを使用してスタイルを適用
    - 列幅を調整
    - _Requirements: 2.2, 2.4, 4.1_

  - [ ]* 5.5 TransportationExcelGeneratorのユニットテストを作成
    - 正常系のテスト（有効なデータでExcelが生成される）
    - 空の経路リストのテスト（エラーが返される）
    - 合計交通費の計算精度をテスト
    - _Requirements: 5.1, 5.2, 5.3_

  - [ ]* 5.6 TransportationExcelGeneratorのプロパティテストを実行
    - **Property 3: 出力ディレクトリへの保存**
    - **Validates: Requirements 1.3**

  - [ ]* 5.7 戻り値構造のプロパティテストを実行
    - **Property 4: 戻り値構造の完全性**
    - **Validates: Requirements 1.4**

- [x] 6. Checkpoint - 全クラスの動作確認
  - 全てのテストが合格することを確認
  - 生成されたExcelファイルの内容を確認
  - 必要に応じてユーザーに質問

- [x] 7. Phase 5: ファサード関数の実装
  - [x] 7.1 receipt_excel_generator()ファサード関数を実装
    - 既存の`receipt_excel_generator()`関数を書き換え
    - @toolデコレータとcontext=Trueを維持
    - 内部でReceiptExcelGeneratorクラスをインスタンス化
    - generator.generate()を呼び出して結果を返す
    - パラメータと戻り値の構造は変更しない
    - _Requirements: 2.1, 2.3, 2.5, 5.1, 5.2, 5.3_

  - [x] 7.2 transportation_excel_generator()ファサード関数を実装
    - 既存の`transportation_excel_generator()`関数を書き換え
    - @toolデコレータとcontext=Trueを維持
    - 内部でTransportationExcelGeneratorクラスをインスタンス化
    - generator.generate()を呼び出して結果を返す
    - パラメータと戻り値の構造は変更しない
    - _Requirements: 2.2, 2.4, 2.5, 5.1, 5.2, 5.3_

  - [ ]* 7.3 既存のテストとの互換性を確認
    - `tests/test_tools.py`のTestExcelGeneratorToolsクラスの全テストを実行
    - 全てのテストが合格することを確認
    - _Requirements: 5.1, 5.2, 5.3_

  - [ ]* 7.4 エラー時の戻り値構造のプロパティテストを実行
    - **Property 6: エラー時の戻り値構造**
    - **Validates: Requirements 3.1, 3.4**

  - [ ]* 7.5 日本語エラーメッセージのプロパティテストを実行
    - **Property 7: 日本語エラーメッセージ**
    - **Validates: Requirements 3.3**

- [x] 8. Phase 6: 既存ヘルパー関数の削除（オプション）
  - [x] 8.1 既存のヘルパー関数を削除
    - 既存の`_get_applicant_name(tool_context)`関数を削除
    - 既存の`_get_application_date(tool_context)`関数を削除
    - 既存の`_generate_filename(prefix)`関数を削除
    - 既存の`_ensure_output_directory()`関数を削除
    - 既存の`_create_workbook(title)`関数を削除
    - 既存の`_create_style_definitions()`関数を削除
    - 既存の`_apply_header_style(cell, styles)`関数を削除
    - 既存の`_apply_title_style(cell, styles)`関数を削除
    - 既存の`_save_workbook(wb, file_path)`関数を削除
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 4.1, 4.2, 4.3_

  - [ ]* 8.2 全てのテストを再実行
    - `tests/test_tools.py`の全テストを実行
    - 新しいユニットテストとプロパティテストを実行
    - 全てのテストが合格することを確認
    - _Requirements: 5.1, 5.2, 5.3_

- [x] 9. 最終チェックポイント - リファクタリング完了確認
  - 全てのテストが合格することを確認
  - コードの重複が削減されていることを確認
  - 既存のエージェント（receipt_expense_agent、travel_agent）との統合が正常に動作することを確認
  - ドキュメント（docstring）が適切に更新されていることを確認
  - 必要に応じてユーザーに最終確認

## Notes

- タスクに`*`マークが付いているものはオプションのテストタスクです。MVPを早く完成させたい場合はスキップできます。
- 各タスクには対応するRequirements番号が記載されています。詳細は`requirements.md`を参照してください。
- チェックポイントタスクでは、全てのテストが合格することを確認し、問題があればユーザーに質問してください。
- Phase 6（既存ヘルパー関数の削除）は完全にオプションです。Phase 5までで後方互換性は維持されます。
- プロパティテストは、Hypothesisライブラリを使用して実装します。
- 既存のテスト（tests/test_tools.py）が全て合格することが、リファクタリング成功の必須条件です。
