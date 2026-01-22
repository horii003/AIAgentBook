# 実装計画: 交通費申請の代行エージェント

## 概要

設計書に基づいて、AWS Strandsを使用したマルチエージェント構成の申請代行システムを実装します。オーケストレーターエージェント（ReceptionAgent）と2つの専門エージェント（TravelAgent、ReceiptExpenseAgent）をAgents as Toolsパターンで構築し、ユーザーとの対話を通じて各種申請書を自動生成します。

## タスク

- [x] 1. 環境セットアップとプロジェクト構造の作成
  - [x] 1.1 AWS CLIのインストールと設定（手動実行）
    - Windows用MSIインストーラーでAWS CLIをインストール
    - `aws configure`を実行してAWS認証情報を設定
    - リージョンを`ap-northeast-1`（東京）に設定
    - ✅ 完了済み
    - _要件: 8.3_
  
  - [x] 1.2 Amazon Bedrockモデルアクセスの確認（手動実行）
    - AWS Management Consoleで利用可能なBedrockモデルへのアクセスを有効化
    - リージョン: ap-northeast-1
    - ✅ 完了済み
    - _要件: 8.2_
  
  - [x] 1.3 Pythonパッケージのインストール
    - requirements.txtを作成
    - strands-agents、strands-agents-tools、strands-agents-builderをインストール
    - hypothesis、pytest、reportlab、openpyxlをインストール
    - ✅ 完了済み
    - _要件: 8.1_
  
  - [x] 1.4 プロジェクト構造の作成
    - agents/、tools/、models/、handlers/、storage/、context/フォルダを作成
    - data/、output/フォルダを作成
    - .envファイルと.gitignoreを作成
    - ✅ 完了済み
    - _要件: 8.4_

- [ ] 2. 運賃データファイルの作成
  - [x] 2.1 電車運賃データファイル（data/train_fares.json）を作成
    - 東京都内の代表的な経路の運賃データを記載
    - _要件: 9.2_
  
  - [x] 2.2 固定運賃データファイル（data/fixed_fares.json）を作成
    - バス、タクシー、飛行機の一定金額を記載
    - _要件: 9.3_

- [ ] 3. データモデルの実装
  - [x] 3.1 RouteDataクラスを実装（models/data_models.py）
    - 経路情報を表すデータクラス
    - _要件: 1.2_
  
  - [x] 3.2 ExpenseReportクラスを実装
    - 申請書データを表すデータクラス
    - to_dict()とto_pdf_content()メソッドを実装
    - _要件: 4.3, 4.5_

- [ ] 4. 交通費精算用ツールの実装
  - [x] 4.1 load_fare_data関数を実装（tools/fare_tools.py）
    - dataフォルダからJSONファイルを読み込む
    - データの妥当性を検証
    - ✅ 完了済み
    - _要件: 9.1, 9.5_
  
  - [x] 4.2 calculate_fare関数を実装（tools/fare_tools.py）
    - 交通手段に応じて運賃データを参照
    - 電車は運賃テーブル、バス/タクシー/飛行機は固定運賃を使用
    - ✅ 完了済み
    - _要件: 2.1, 2.5, 2.6_
  
  - [x] 4.3 validate_input関数を実装（tools/validation_tools.py）
    - 日付、場所、費用の検証ロジック
    - エラーメッセージの生成
    - ✅ 完了済み
    - _要件: 7.1, 7.2, 7.3_
  
  - [x] 4.4 generate_report関数を実装（tools/report_tools.py）
    - PDF生成機能（reportlab使用）
    - JSON生成機能
    - Outputフォルダへの保存
    - ファイル名生成と競合処理
    - ✅ 完了済み
    - _要件: 4.3, 4.5, 5.1, 5.2, 5.3, 5.5, 5.6_
  
  - [ ] 4.5 交通費精算ツールのプロパティテストを実装
    - **プロパティ5: 運賃データ参照の正確性**
    - **プロパティ7: 複数交通手段の合算**
    - **プロパティ11: 申請書の完全性**
    - **プロパティ16-20: 入力検証**
    - **プロパティ21: 運賃データファイル不在時のエラー処理**
    - **検証: 要件 2.1, 2.5, 2.6, 2.7, 4.3, 4.5, 7.1-7.5, 9.4**

- [ ] 5. 領収書精算用ツールの実装
  - [x] 5.1 ConfigManagerクラスを実装（storage/config_manager.py）
    - 環境変数からの設定読み込み
    - 申請者名、出力ディレクトリの管理
    - ✅ 完了済み
  
  - [x] 5.2 承認ルールエンジンを実装（handlers/approval_rules.py）
    - 30,000円上限チェック
    - ✅ 完了済み
  
  - [x] 5.3 excel_generator関数を実装（tools/excel_generator.py）
    - openpyxlを使用してExcel申請書を生成
    - 承認ルールの適用
    - ✅ 完了済み
  
  - [x] 5.4 config_updater関数を実装（tools/config_update.py）
    - 申請者名や出力ディレクトリの設定更新
    - ✅ 完了済み
  
  - [ ] 5.5 領収書精算ツールのプロパティテストを実装
    - Excel生成の正確性テスト
    - 承認ルールの検証テスト

- [ ] 6. 専門エージェント1: TravelAgentの実装
  - [x] 6.1 TravelAgentをAgents as Tools形式で実装（agents/travel_agent.py）
    - シングルトンパターンで実装
    - SlidingWindowConversationManagerで会話履歴を管理
    - @toolデコレータでツール化
    - システムプロンプトの設定
    - ✅ 完了済み
    - _要件: 1.1, 1.5, 8.1, 8.2_
  
  - [x] 6.2 ツールの登録
    - calculate_fare、validate_input、generate_reportを登録
    - ✅ 完了済み
    - _要件: 8.1_
  
  - [x] 6.3 reset_travel_agent関数を実装
    - 会話履歴のリセット機能
    - ✅ 完了済み
  
  - [ ] 6.4 TravelAgentのプロパティテストを実装
    - **プロパティ1-4: 経路データ抽出、フォローアップ、明確化、コンテキスト維持**
    - **プロパティ6: 一区間ごとの処理フロー**
    - **検証: 要件 1.2, 1.3, 1.4, 1.5, 2.2, 2.3, 2.4**

- [ ] 7. 専門エージェント2: ReceiptExpenseAgentの実装
  - [x] 7.1 ReceiptExpenseAgentをAgents as Tools形式で実装（agents/receipt_expense_agent.py）
    - シングルトンパターンで実装
    - SlidingWindowConversationManagerで会話履歴を管理
    - @toolデコレータでツール化
    - システムプロンプトの設定
    - ✅ 完了済み
  
  - [x] 7.2 ツールの登録
    - image_reader、excel_generator、config_updaterを登録
    - ✅ 完了済み
  
  - [x] 7.3 ConfigManagerの初期化
    - エージェント初期化時にConfigManagerを設定
    - ✅ 完了済み
  
  - [x] 7.4 reset_receipt_expense_agent関数を実装
    - 会話履歴のリセット機能
    - ✅ 完了済み
  
  - [ ] 7.5 ReceiptExpenseAgentのプロパティテストを実装
    - 画像情報抽出の正確性テスト
    - 経費区分判断のテスト

- [ ] 8. オーケストレーターエージェント: ReceptionAgentの実装
  - [x] 8.1 ReceptionAgentクラスを実装（agents/reception_agent.py）
    - システムプロンプトの設定
    - 専門エージェントの振り分けロジック
    - ✅ 完了済み
  
  - [x] 8.2 専門エージェントの登録
    - travel_agentとreceipt_expense_agentをツールとして登録
    - ✅ 完了済み
  
  - [x] 8.3 対話ループの実装
    - ユーザー入力の受付
    - 終了処理（exit/quit）
    - リセット処理（reset）
    - ✅ 完了済み
  
  - [ ] 8.4 オーケストレーターのプロパティテストを実装
    - 申請内容の分類精度テスト
    - 適切なエージェントへの振り分けテスト

- [ ] 9. エラーハンドリングの実装
  - [x] 9.1 エラーハンドラーを実装（handlers/error_handler.py）
    - Bedrock接続エラー
    - 運賃データ読み込みエラー
    - 計算エラー
    - ファイル保存エラー
    - 入力検証エラー
    - ✅ 完了済み
    - _要件: 6.1, 6.2, 6.3_
  
  - [x] 9.2 エラーログ機能を実装
    - ログフォーマットの定義
    - ファイルへのログ出力
    - ✅ 完了済み
    - _要件: 6.5_
  
  - [ ] 9.3 エラーハンドリングのプロパティテストを実装
    - **プロパティ14: エラー時の状態保持**
    - **プロパティ15: エラーログの記録**
    - **検証: 要件 6.4, 6.5**

- [ ] 10. メインエントリーポイントの実装
  - [x] 10.1 main.pyを実装
    - ReceptionAgentの初期化
    - 対話ループの開始
    - ✅ 完了済み
    - _要件: 1.1_
  
  - [ ] 10.2 統合テストを実装
    - エンドツーエンドの対話フロー
    - 交通費精算: 一区間の入力から申請書生成まで
    - 領収書精算: 画像読み込みから申請書生成まで
    - オーケストレーション: 複数エージェントの連携
    - _要件: 1.1, 2.2, 2.3, 3.1, 4.1, 5.1_

- [ ] 11. チェックポイント - 最終確認
  - すべてのテストが通ることを確認
  - 実際にシステムを起動して動作確認
  - マルチエージェント連携の確認
  - ユーザーに質問があれば確認

## 注記

- すべてのタスクは必須です（包括的な開発アプローチ）
- 各タスクは要件番号を参照しており、トレーサビリティを確保しています
- チェックポイントで段階的に検証を行い、問題を早期に発見します
- プロパティテストは最低100回のイテレーションで実行します
- すべてのプロパティテストには設計書のプロパティ番号を明記します
