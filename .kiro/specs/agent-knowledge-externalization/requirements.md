# 要件定義書

## はじめに

このドキュメントは、交通費申請および経費申請エージェントのプロンプトファイルに埋め込まれているルールを外部ファイルに分離する機能の要件を定義します。現在、申請ルール（日付チェック、金額チェック、業務目的チェックなど）がプロンプトコードに直接埋め込まれており、ルール変更時にコード修正が必要となっています。この機能により、ルールを外部ファイルとして管理し、保守性と柔軟性を向上させます。

## 用語集

- **System**: エージェント知識外部化システム
- **Policy_File**: agent_knowledgeフォルダ内のルール定義ファイル
- **Prompt_Generator**: プロンプト生成関数（_get_travel_system_prompt、_get_receipt_expense_system_prompt）
- **Travel_Agent**: 交通費申請エージェント
- **Receipt_Agent**: 経費申請エージェント
- **Rule**: 申請処理における検証ルール（日付チェック、金額チェック、業務目的チェック）

## 要件

### 要件1: ポリシーファイルの作成

**ユーザーストーリー:** 開発者として、外部ポリシーファイルを作成したい。そうすることで、申請ルールをコードと分離して管理できる。

#### 受入基準

1. THE System SHALL agent_knowledge/travel_policies.pyを作成し、交通費申請ルールを含める
2. THE System SHALL agent_knowledge/receipt_policies.pyを作成し、経費申請ルールを含める
3. WHEN Policy_Fileが作成される THEN THE System SHALL 設定可能な閾値を持つ日付検証ルールを含める
4. WHEN Policy_Fileが作成される THEN THE System SHALL 設定可能な閾値を持つ金額検証ルールを含める
5. WHEN Policy_Fileが作成される THEN THE System SHALL 業務目的検証ルールを含める
6. THE System SHALL 各Ruleを構造化されたデータ形式（辞書またはクラス）として定義する

### 要件2: ルールの構造化

**ユーザーストーリー:** 開発者として、ルールを一貫した構造で定義したい。そうすることで、ルールを理解しやすく、修正しやすくできる。

#### 受入基準

1. WHEN 日付検証ルールを定義する THEN THE System SHALL 期間閾値（例：3ヶ月）を含める
2. WHEN 金額検証ルールを定義する THEN THE System SHALL 金額閾値と承認要件を含める
3. WHEN 業務目的ルールを定義する THEN THE System SHALL 検証基準とエラーメッセージを含める
4. THE System SHALL 各Ruleに日本語のエラーメッセージを提供する
5. THE System SHALL 各Ruleに日本語のユーザープロンプトを提供する
6. FOR ALL Rules, THE System SHALL ルール識別子と説明を含める

### 要件3: プロンプト生成関数の修正

**ユーザーストーリー:** 開発者として、プロンプト生成関数がルールを動的に読み込むようにしたい。そうすることで、ルール変更時にコード修正が不要になる。

#### 受入基準

1. WHEN Prompt_Generatorが実行される THEN THE System SHALL Policy_Fileからルールをインポートする
2. WHEN Prompt_Generatorがプロンプトを生成する THEN THE System SHALL 読み込んだルールをプロンプトテキストに注入する
3. THE System SHALL 現在のプロンプト構造とフォーマットを維持する
4. WHEN Policy_Fileが存在しない THEN THE System SHALL 明確なエラーメッセージを発生させる
5. WHEN Policy_Fileに無効なデータが含まれる THEN THE System SHALL 検証エラーを発生させる

### 要件4: 後方互換性の保持

**ユーザーストーリー:** 開発者として、リファクタリングが既存の動作を維持するようにしたい。そうすることで、現在の機能を壊さないようにできる。

#### 受入基準

1. WHEN Systemが外部ルールを読み込む THEN 生成されたプロンプト SHALL 現在の埋め込みバージョンと機能的に同等である
2. WHEN Travel_Agentが実行される THEN THE System SHALL リファクタリング前と同じ検証ロジックを適用する
3. WHEN Receipt_Agentが実行される THEN THE System SHALL リファクタリング前と同じ検証ロジックを適用する
4. THE System SHALL 現在の日付計算ロジック（today、three_months_ago）をすべて保持する
5. THE System SHALL 現在のエラーハンドリング動作をすべて保持する

### 要件5: ルールの読み込み機能

**ユーザーストーリー:** 開発者として、再利用可能なルール読み込み機構を持ちたい。そうすることで、将来的に新しいポリシーファイルを簡単に追加できる。

#### 受入基準

1. THE System SHALL Policy_Fileからルールを読み込む関数を提供する
2. WHEN ルールを読み込む THEN THE System SHALL ルール構造を検証する
3. WHEN ルールを読み込む THEN THE System SHALL ファイル未検出エラーを適切に処理する
4. WHEN ルールを読み込む THEN THE System SHALL JSON/Python解析エラーを適切に処理する
5. THE System SHALL 読み込んだルールをキャッシュし、繰り返しのファイルI/O操作を回避する

### 要件6: ドキュメントとテスト

**ユーザーストーリー:** 開発者として、明確なドキュメントとテストを持ちたい。そうすることで、新しい構造を理解し、検証できる。

#### 受入基準

1. THE System SHALL すべてのPolicy_Fileモジュールにルール構造を説明するdocstringを含める
2. THE System SHALL Policy_FileのdocstringにUsage exampleを含める
3. WHEN ルールが修正される THEN THE System SHALL Policy_Fileの更新方法に関する明確な指示を提供する
4. THE System SHALL ルール読み込み機能を検証するユニットテストを含める
5. THE System SHALL 外部ルールを使用したプロンプト生成を検証する統合テストを含める
