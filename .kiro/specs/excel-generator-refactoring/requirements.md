# Requirements Document

## Introduction

このドキュメントは、`tools/excel_generator.py`のリファクタリングに関する要件を定義します。現在、このモジュールには2つの独立した関数（`receipt_excel_generator`と`travel_excel_generator`）が存在し、多くの共通コードが重複しています。このリファクタリングの目的は、コードの重複を削減し、保守性を向上させることです。

## Glossary

- **Excel_Generator**: Excel形式の申請書を生成するツールモジュール
- **Receipt_Excel_Generator**: 経費精算申請書（領収書ベース）を生成する関数
- **Travel_Excel_Generator**: 交通費申請書（経路データベース）を生成する関数
- **Unified_Generator**: リファクタリング後の統合されたExcel生成関数
- **Tool_Context**: AWS Strandsフレームワークが提供するコンテキストオブジェクト
- **Invocation_State**: ツール実行時の状態情報（申請者名などを含む）
- **Agent**: Excel生成ツールを呼び出すエージェント（receipt_expense_agent、travel_agent）
- **Output_Directory**: 生成されたExcelファイルを保存するディレクトリ（output/）
- **Openpyxl**: PythonでExcelファイルを操作するためのライブラリ

## Requirements

### Requirement 1: 共通機能の統合

**User Story:** 開発者として、重複したコードを削減したいので、2つのExcel生成関数の共通機能を統合したい

#### Acceptance Criteria

1. THE Unified_Generator SHALL 申請者名をInvocation_Stateから取得する
2. THE Unified_Generator SHALL タイムスタンプ付きのファイル名を生成する
3. THE Unified_Generator SHALL Output_Directoryにファイルを保存する
4. THE Unified_Generator SHALL 成功/失敗を示す辞書を返す
5. THE Unified_Generator SHALL 共通のスタイル設定（フォント、色、配置）を適用する

### Requirement 2: 既存機能の互換性維持

**User Story:** システム管理者として、既存のエージェントが正常に動作し続けることを保証したいので、既存のツールインターフェースを維持したい

#### Acceptance Criteria

1. WHEN Receipt_Expense_Agent calls Receipt_Excel_Generator, THEN THE Excel_Generator SHALL 経費精算申請書を生成する
2. WHEN Travel_Agent calls Travel_Excel_Generator, THEN THE Excel_Generator SHALL 交通費申請書を生成する
3. THE Receipt_Excel_Generator SHALL 以下のパラメータを受け取る: store_name, amount, date, items, expense_category, tool_context
4. THE Travel_Excel_Generator SHALL 以下のパラメータを受け取る: routes, tool_context
5. THE Excel_Generator SHALL @toolデコレータとcontext=Trueを使用する

### Requirement 3: エラーハンドリングの一貫性

**User Story:** 開発者として、エラー処理を統一したいので、すべてのExcel生成関数で一貫したエラーハンドリングを実装したい

#### Acceptance Criteria

1. WHEN バリデーションエラーが発生した場合, THEN THE Excel_Generator SHALL エラーメッセージを含む辞書を返す
2. WHEN ファイル保存に失敗した場合, THEN THE Excel_Generator SHALL エラーメッセージを含む辞書を返す
3. THE Excel_Generator SHALL すべてのエラーメッセージを日本語で返す
4. THE Excel_Generator SHALL success=Falseのフラグを含む辞書を返す

### Requirement 4: コード構造の改善

**User Story:** 開発者として、コードの可読性と保守性を向上させたいので、明確な責任分離を持つ関数構造を実装したい

#### Acceptance Criteria

1. THE Excel_Generator SHALL Excel生成ロジックを再利用可能なヘルパー関数に分離する
2. THE Excel_Generator SHALL スタイル設定を共通関数として実装する
3. THE Excel_Generator SHALL ファイル名生成ロジックを共通関数として実装する
4. THE Excel_Generator SHALL 各関数が単一の責任を持つように設計する

### Requirement 5: テストの互換性維持

**User Story:** 開発者として、既存のテストが引き続き動作することを保証したいので、テストコードへの影響を最小限に抑えたい

#### Acceptance Criteria

1. WHEN リファクタリング後にテストを実行した場合, THEN THE Excel_Generator SHALL すべての既存テストに合格する
2. THE Excel_Generator SHALL tests/test_tools.pyのTestExcelGeneratorToolsクラスと互換性を保つ
3. THE Excel_Generator SHALL 同じ戻り値の構造（success, file_path, message, total_cost）を維持する

### Requirement 6: ドキュメントの更新

**User Story:** 開発者として、リファクタリング後のコードを理解したいので、適切なドキュメントとコメントを提供したい

#### Acceptance Criteria

1. THE Excel_Generator SHALL 各関数にdocstringを含める
2. THE Excel_Generator SHALL パラメータと戻り値の説明を含める
3. THE Excel_Generator SHALL モジュールレベルのドキュメントを更新する
4. THE Excel_Generator SHALL 日本語でドキュメントを記述する
