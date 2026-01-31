# Implementation Plan: Excel Generator Refactoring

## Overview

このタスクリストは、`tools/excel_generator.py`のリファクタリングを段階的に実装するための計画です。共通機能をヘルパー関数に抽出し、コードの重複を削減しながら、既存のエージェントとの完全な互換性を維持します。

各タスクは、前のタスクの成果物を基に構築され、段階的に機能を検証します。テスト関連のサブタスクはオプションとしてマークされており、コア機能の実装を優先できます。

## Tasks

- [x] 1. 共通ヘルパー関数の実装
  - [x] 1.1 申請者名取得関数を実装する
    - `_get_applicant_name(tool_context)`関数を作成
    - ToolContextからinvocation_stateを安全に取得
    - 申請者名が存在しない場合は"未設定"を返す
    - docstringを日本語で記述
    - _Requirements: 1.1, 4.1_
  
  - [ ]* 1.2 申請者名取得のプロパティテストを作成する
    - **Property 1: 申請者名の正確な取得**
    - **Validates: Requirements 1.1**
    - Hypothesisを使用してランダムなToolContextを生成
    - invocation_stateあり/なしの両方のケースをテスト
    - 最低100イテレーションで実行
  
  - [x] 1.3 ファイル名生成関数を実装する
    - `_generate_filename(prefix)`関数を作成
    - datetimeを使用してYYYYMMDD_HHMMSS形式のタイムスタンプを生成
    - フォーマット: `{prefix}_YYYYMMDD_HHMMSS.xlsx`
    - docstringを日本語で記述
    - _Requirements: 1.2, 4.3_
  
  - [ ]* 1.4 ファイル名生成のプロパティテストを作成する
    - **Property 2: ファイル名フォーマットの一貫性**
    - **Validates: Requirements 1.2**
    - ランダムなプレフィックス文字列を生成
    - 正規表現で`{prefix}_\d{8}_\d{6}\.xlsx`パターンを検証
    - 最低100イテレーションで実行
  
  - [x] 1.5 出力ディレクトリ確保関数を実装する
    - `_ensure_output_directory()`関数を作成
    - Pathlibを使用してoutput/ディレクトリを作成
    - 既に存在する場合はスキップ
    - Pathオブジェクトを返す
    - docstringを日本語で記述
    - _Requirements: 1.3, 4.1_

- [x] 2. Excelワークブック関連のヘルパー関数を実装する
  - [x] 2.1 ワークブック作成関数を実装する
    - `_create_workbook(title)`関数を作成
    - openpyxlを使用してWorkbookとWorksheetを作成
    - ワークシートのタイトルを設定
    - tuple[Workbook, Worksheet]を返す
    - docstringを日本語で記述
    - _Requirements: 1.3, 4.1_
  
  - [x] 2.2 スタイル定義作成関数を実装する
    - `_create_style_definitions()`関数を作成
    - Font、PatternFill、Alignmentオブジェクトを作成
    - ヘッダー用: 太字12pt、#CCE5FF背景、中央揃え
    - タイトル用: 太字14pt、中央揃え
    - ラベル用: 太字12pt、#CCE5FF背景
    - データ用: 中央揃え、右揃え
    - 合計用: 太字12pt、右揃え
    - 全てのスタイルを含む辞書を返す
    - docstringを日本語で記述
    - _Requirements: 1.5, 4.2_
  
  - [ ]* 2.3 スタイル定義のプロパティテストを作成する
    - **Property 5: スタイル定義の完全性**
    - **Validates: Requirements 1.5**
    - 返される辞書が全ての必須キーを含むことを検証
    - 各値が適切なopenpyxlオブジェクト型であることを確認
    - 最低100イテレーションで実行
  
  - [x] 2.4 スタイル適用関数を実装する
    - `_apply_header_style(cell, styles)`関数を作成
    - `_apply_title_style(cell, styles)`関数を作成
    - セルにフォント、背景色、配置を一括適用
    - docstringを日本語で記述
    - _Requirements: 1.5, 4.1_
  
  - [x] 2.5 ワークブック保存関数を実装する
    - `_save_workbook(wb, file_path)`関数を作成
    - try-exceptでIOError、PermissionErrorをキャッチ
    - 成功時はTrue、失敗時はFalseを返す
    - docstringを日本語で記述
    - _Requirements: 1.3, 3.2, 4.1_

- [x] 3. Checkpoint - ヘルパー関数の動作確認
  - 全てのヘルパー関数が正しく動作することを確認
  - 基本的なユニットテストを実行
  - 質問があればユーザーに確認

- [x] 4. receipt_excel_generatorのリファクタリング
  - [x] 4.1 receipt_excel_generatorを共通ヘルパー関数を使用するように書き換える
    - `_get_applicant_name()`を使用して申請者名を取得
    - `_generate_filename("経費精算申請書")`を使用
    - `_ensure_output_directory()`を使用
    - `_create_workbook("経費精算申請書")`を使用
    - `_create_style_definitions()`を使用
    - 領収書固有のロジック（金額チェック、品目リスト）は保持
    - `_save_workbook()`を使用
    - 既存のインターフェース（パラメータ、戻り値）を維持
    - _Requirements: 2.1, 2.3, 4.1, 5.3_
  
  - [ ]* 4.2 receipt_excel_generatorのユニットテストを実行する
    - tests/test_tools.pyの既存テストを実行
    - 全てのテストが合格することを確認
    - _Requirements: 5.1, 5.2_
  
  - [ ]* 4.3 戻り値構造のプロパティテストを作成する（receipt用）
    - **Property 4: 戻り値構造の完全性**
    - **Validates: Requirements 1.4**
    - ランダムな有効/無効入力データを生成
    - 戻り値がsuccess、file_path、messageキーを含むことを検証
    - 最低100イテレーションで実行

- [x] 5. travel_excel_generatorのリファクタリング
  - [x] 5.1 travel_excel_generatorを共通ヘルパー関数を使用するように書き換える
    - `_get_applicant_name()`を使用して申請者名を取得
    - `_generate_filename("交通費申請書")`を使用
    - `_ensure_output_directory()`を使用
    - `_create_workbook("交通費申請書")`を使用
    - `_create_style_definitions()`を使用
    - 交通費固有のロジック（経路テーブル、合計計算）は保持
    - `_save_workbook()`を使用
    - 既存のインターフェース（パラメータ、戻り値）を維持
    - _Requirements: 2.2, 2.4, 4.1, 5.3_
  
  - [ ]* 5.2 travel_excel_generatorのユニットテストを実行する
    - tests/test_tools.pyの既存テストを実行
    - 全てのテストが合格することを確認
    - _Requirements: 5.1, 5.2_
  
  - [ ]* 5.3 戻り値構造のプロパティテストを作成する（travel用）
    - **Property 4: 戻り値構造の完全性**
    - **Validates: Requirements 1.4**
    - ランダムな有効/無効入力データを生成
    - 戻り値がsuccess、file_path、total_cost、messageキーを含むことを検証
    - 最低100イテレーションで実行
  
  - [ ]* 5.4 出力ディレクトリ保存のプロパティテストを作成する
    - **Property 3: 出力ディレクトリへの保存**
    - **Validates: Requirements 1.3**
    - ランダムな有効入力データを生成
    - 成功時のfile_pathが"output/"で始まることを検証
    - 最低100イテレーションで実行

- [x] 6. エラーハンドリングのテスト
  - [ ]* 6.1 エラー時の戻り値構造のプロパティテストを作成する
    - **Property 6: エラー時の戻り値構造**
    - **Validates: Requirements 3.1**
    - ランダムな不正入力データを生成（空リスト、不正日付など）
    - success=False、messageが非空、file_pathが空であることを検証
    - 最低100イテレーションで実行
  
  - [ ]* 6.2 日本語エラーメッセージのプロパティテストを作成する
    - **Property 7: 日本語エラーメッセージ**
    - **Validates: Requirements 3.3**
    - ランダムなエラーケースを生成
    - messageに日本語文字（ひらがな、カタカナ、漢字）が含まれることを検証
    - 正規表現で日本語文字範囲をチェック
    - 最低100イテレーションで実行
  
  - [ ]* 6.3 エラーハンドリングのユニットテストを作成する
    - 空の経路リストでエラーが返されることをテスト
    - 不正な日付フォーマットでバリデーションエラーが発生することをテスト
    - ファイル保存失敗時のエラーハンドリングをテスト
    - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [x] 7. ドキュメントの更新
  - [x] 7.1 モジュールレベルのdocstringを更新する
    - リファクタリング後の構造を説明
    - 共通ヘルパー関数の一覧を記載
    - 公開ツール関数の使用方法を説明
    - 日本語で記述
    - _Requirements: 6.1, 6.3, 6.4_
  
  - [x] 7.2 各関数のdocstringを確認・更新する
    - 全ての関数にdocstringが存在することを確認
    - パラメータと戻り値の説明が正確であることを確認
    - 日本語で記述されていることを確認
    - _Requirements: 6.1, 6.2, 6.4_

- [x] 8. Final Checkpoint - 統合テストと最終確認
  - 全てのユニットテストを実行して合格を確認
  - 全てのプロパティテストを実行して合格を確認
  - tests/test_tools.pyの既存テストが全て合格することを確認
  - コードカバレッジを確認（目標: 行90%以上、分岐85%以上）
  - 質問があればユーザーに確認

## Notes

- `*`マークが付いたタスクはオプションで、より速いMVPのためにスキップ可能です
- 各タスクは具体的な要件を参照しており、トレーサビリティを確保しています
- チェックポイントで段階的な検証を行います
- プロパティテストは普遍的な正確性プロパティを検証します
- ユニットテストは特定の例とエッジケースを検証します
- 既存のテストとの互換性を維持することで、エージェントの動作が保証されます
