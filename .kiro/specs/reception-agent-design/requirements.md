# Requirements Document

## Introduction

申請受付窓口エージェント（reception_agent）は、社内の様々な申請プロセスの入口として機能するインテリジェントなオーケストレーターです。社員が「出張したい」「備品を購入したい」などの申請内容を入力すると、その内容を分析し、適切な専門エージェント（交通費精算申請エージェント、経費精算申請エージェント）に自動的に振り分けます。

このエージェントの目的は、申請ルールや申請方法が分からない社員でも、正しく申請できるようにすることです。

## Glossary

- **Reception_Agent**: 申請受付窓口エージェント。ユーザーからの申請内容を受け付け、適切な専門エージェントに振り分けるオーケストレーター
- **Travel_Agent**: 交通費精算申請エージェント。顧客訪問や出張などに発生した交通費の精算を処理する専門エージェント
- **Receipt_Expense_Agent**: 経費精算申請エージェント。領収書画像を使った経費精算を処理する専門エージェント
- **Applicant**: 申請者。申請を行う社員
- **Invocation_State**: エージェント間で共有される状態情報。申請者名などのコンテキスト情報を保持
- **Conversation_Manager**: 会話履歴を管理するコンポーネント。SlidingWindowConversationManagerを使用
- **System_Prompt**: エージェントの役割と動作を定義するプロンプト
- **Agent_as_Tool**: エージェントをツールとして他のエージェントから呼び出せるようにするパターン

## Requirements

### カテゴリ1: エージェント定義

### Requirement 1: 申請内容の受付と分類

**User Story:** As a 社員, I want to 申請内容をキーワードや自然な日本語で入力する, so that 申請の種類を意識せずに申請を開始できる

#### Acceptance Criteria

1. WHEN ユーザーが申請内容を入力する THEN THE Reception_Agent SHALL その内容を受け付けて分析する
2. WHEN 申請内容が交通費に関連する THEN THE Reception_Agent SHALL Travel_Agentに振り分けを判断する
3. WHEN 申請内容が経費精算に関連する THEN THE Reception_Agent SHALL Receipt_Expense_Agentに振り分けを判断する
4. WHEN 申請内容が曖昧である THEN THE Reception_Agent SHALL ユーザーに追加情報を質問する

### Requirement 2: 専門エージェントへの振り分け

**User Story:** As a Reception_Agent, I want to 申請内容を適切な専門エージェントに振り分ける, so that 各申請が正しく処理される

#### Acceptance Criteria

1. WHEN 交通費精算が必要と判断される THEN THE Reception_Agent SHALL Travel_Agentツールを呼び出す
2. WHEN 経費精算が必要と判断される THEN THE Reception_Agent SHALL Receipt_Expense_Agentツールを呼び出す
3. WHEN 専門エージェントを呼び出す THEN THE Reception_Agent SHALL invocation_stateに申請者名を含める
4. WHEN 専門エージェントから応答を受け取る THEN THE Reception_Agent SHALL その応答をユーザーに伝える

### Requirement 3: 申請者情報の管理

**User Story:** As a Reception_Agent, I want to 申請者情報を一度だけ収集して保持する, so that ユーザーが毎回入力する手間を省ける

#### Acceptance Criteria

1. WHEN エージェントが初めて実行される THEN THE Reception_Agent SHALL 申請者名の入力を要求する
2. WHEN 申請者名が入力される THEN THE Reception_Agent SHALL その情報を保持する
3. WHEN 申請者名が空である THEN THE Reception_Agent SHALL 再入力を要求する
4. WHEN 専門エージェントを呼び出す THEN THE Reception_Agent SHALL 保持している申請者名をinvocation_stateとして渡す
5. WHEN リセットコマンドが実行される THEN THE Reception_Agent SHALL 申請者情報をクリアする

### Requirement 4: 対話ループの制御

**User Story:** As a 社員, I want to 複数の申請を連続して処理する, so that 一度のセッションで複数の申請を完了できる

#### Acceptance Criteria

1. WHEN 専門エージェントの処理が完了する THEN THE Reception_Agent SHALL ユーザーに他の申請の有無を確認する
2. WHEN ユーザーが追加の申請を希望する THEN THE Reception_Agent SHALL 新しい申請内容の入力を受け付ける
3. WHEN ユーザーが終了を希望する THEN THE Reception_Agent SHALL 対話ループを終了する
4. WHEN ユーザーが空入力を行う THEN THE Reception_Agent SHALL それをスキップして次の入力を待つ

### Requirement 5: コマンド処理

**User Story:** As a 社員, I want to 特定のコマンドでエージェントを制御する, so that 必要に応じて終了やリセットができる

#### Acceptance Criteria

1. WHEN ユーザーが "exit" または "quit" を入力する THEN THE Reception_Agent SHALL 対話を終了する
2. WHEN ユーザーが "reset" を入力する THEN THE Reception_Agent SHALL 会話履歴と申請者情報をリセットする
3. WHEN リセットが実行される THEN THE Reception_Agent SHALL すべての専門エージェントの状態もリセットする
4. WHEN リセット後 THEN THE Reception_Agent SHALL 申請者情報の再入力を要求する

### Requirement 6: エラーハンドリング

**User Story:** As a Reception_Agent, I want to エラーを適切に処理する, so that システムが安定して動作する

#### Acceptance Criteria

1. WHEN 専門エージェントでエラーが発生する THEN THE Reception_Agent SHALL エラーメッセージをユーザーに表示する
2. WHEN KeyboardInterruptが発生する THEN THE Reception_Agent SHALL 処理を中断して終了する
3. WHEN 予期しない例外が発生する THEN THE Reception_Agent SHALL エラーメッセージを表示して対話を継続する
4. WHEN エラー後 THEN THE Reception_Agent SHALL ユーザーに再試行を促す

### Requirement 7: 会話履歴の管理

**User Story:** As a Reception_Agent, I want to 会話履歴を適切に管理する, so that 複数エージェントとのやり取りを保持できる

#### Acceptance Criteria

1. THE Reception_Agent SHALL SlidingWindowConversationManagerを使用する
2. THE Reception_Agent SHALL ウィンドウサイズを30に設定する
3. THE Reception_Agent SHALL 結果の切り詰めを有効にする
4. THE Reception_Agent SHALL ターン単位ではなく全体で履歴を管理する

### Requirement 8: AWS Bedrockとの統合

**User Story:** As a Reception_Agent, I want to AWS Bedrockの言語モデルを使用する, so that 高度な自然言語理解を実現できる

#### Acceptance Criteria

1. THE Reception_Agent SHALL Claude Sonnet 4.5モデル（jp.anthropic.claude-sonnet-4-5-20250929-v1:0）を使用する
2. THE Reception_Agent SHALL ModelRetryStrategyを設定する
3. THE Reception_Agent SHALL 最大6回のリトライを許可する
4. THE Reception_Agent SHALL 初期遅延4秒、最大遅延240秒のリトライ戦略を使用する

### Requirement 9: ユーザーインターフェース

**User Story:** As a 社員, I want to 分かりやすいインターフェースで対話する, so that スムーズに申請を進められる

#### Acceptance Criteria

1. WHEN エージェントが起動する THEN THE Reception_Agent SHALL ウェルカムメッセージを表示する
2. WHEN エージェントが起動する THEN THE Reception_Agent SHALL 使用方法の説明を表示する
3. WHEN ユーザー入力を待つ THEN THE Reception_Agent SHALL プロンプトを表示する
4. WHEN エージェントが応答する THEN THE Reception_Agent SHALL "エージェント: "プレフィックスを付けて表示する
5. THE Reception_Agent SHALL 常に丁寧で分かりやすい日本語で対話する

### Requirement 10: シングルトンパターンの実装

**User Story:** As a システム, I want to Reception_Agentインスタンスを適切に管理する, so that リソースを効率的に使用できる

#### Acceptance Criteria

1. THE Reception_Agent SHALL クラスベースの実装を使用する
2. WHEN インスタンスが作成される THEN THE Reception_Agent SHALL 初期化処理を実行する
3. WHEN 複数回実行される THEN THE Reception_Agent SHALL 同じインスタンスの状態を保持する
4. WHEN リセットが要求される THEN THE Reception_Agent SHALL 内部状態をクリアする
