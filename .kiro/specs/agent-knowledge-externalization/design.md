# 設計ドキュメント

## 概要

このドキュメントは、交通費申請および経費申請エージェントのプロンプトファイルに埋め込まれているルールを外部ファイルに分離する機能の設計を定義します。現在のシステムでは、申請ルール（日付チェック、金額チェック、業務目的チェック）がプロンプト生成関数内にハードコードされており、ルール変更時にコード修正が必要です。この設計により、ルールテキストを外部ファイル（agent_knowledgeフォルダ）に分離し、動的に読み込む仕組みを実装します。

## アーキテクチャ

### 現在の構造

```
prompt/
├── prompt_travel.py
│   └── _get_travel_system_prompt() # ルールテキストが埋め込まれている
└── prompt_receipt.py
    └── _get_receipt_expense_system_prompt() # ルールテキストが埋め込まれている
```

### 新しい構造

```
agent_knowledge/
├── __init__.py
├── travel_policies.py      # 交通費申請ルールテキスト
└── receipt_policies.py     # 経費申請ルールテキスト

prompt/
├── prompt_travel.py
│   └── _get_travel_system_prompt() # 外部ルールを読み込む
└── prompt_receipt.py
    └── _get_receipt_expense_system_prompt() # 外部ルールを読み込む
```

### データフロー

```mermaid
graph LR
    A[エージェント起動] --> B[プロンプト生成関数呼び出し]
    B --> C[ポリシーファイルからルールテキストをインポート]
    C --> D[日付情報を計算]
    D --> E[ルールテキストに日付を注入]
    E --> F[完成したプロンプト返却]
```

## コンポーネントとインターフェース

### 1. ポリシーファイル（travel_policies.py、receipt_policies.py）

各ポリシーファイルは、ルールテキストを文字列として提供します。プロンプト生成時に日付などの動的な値を注入できるように、Pythonのf-string形式で定義します。

```python
# agent_knowledge/travel_policies.py

def get_travel_rules(today: str, three_months_ago: str) -> str:
    """
    交通費申請ルールテキストを取得
    
    Args:
        today: 今日の日付（YYYY-MM-DD形式）
        three_months_ago: 3ヶ月前の日付（YYYY-MM-DD形式）
    
    Returns:
        ルールテキスト
    """
    return f"""## 交通費申請ルール（必須チェック項目）
1. 日付チェック
- 日付が {three_months_ago} より前（3ヶ月を超える）の場合：
* まず、ユーザーに日付の確認と修正を提案してください
* 修正されない場合は、業務上の正当な理由を確認してください
* 正当な理由がない場合は申請を受け付けないでください

- 日付が {three_months_ago} ～{today}の範囲である場合：
* 日付チェックは問題ありません（次のステップに進んでください）

2. 金額チェック
- 10,000円を超える申請の場合は、必ず事前に上長の承認を得ているか確認してください
* ユーザーに詳細の確認は不要です。承認の有無だけ確認してください
* 承認を得ていない場合は、先に上長の承認を取得するよう案内してください
"""
```

```python
# agent_knowledge/receipt_policies.py

def get_receipt_rules(today: str, three_months_ago: str) -> str:
    """
    経費申請ルールテキストを取得
    
    Args:
        today: 今日の日付（YYYY-MM-DD形式）
        three_months_ago: 3ヶ月前の日付（YYYY-MM-DD形式）
    
    Returns:
        ルールテキスト
    """
    return f"""## 経費申請ルール（必須チェック項目）
1. 日付チェック
- 領収書の日付が {three_months_ago} より前（3ヶ月を超える）の場合：
* まず、ユーザーに日付の確認と修正を提案してください
* 修正されない場合は、業務上の正当な理由を確認してください
* 正当な理由がない場合は申請を受け付けないでください
- 領収書の日付が {three_months_ago} ～{today}の範囲である場合：
* 日付チェックは問題ありません（次のステップに進んでください）

2. 金額チェック
- 5,000円を超える申請の場合は、必ず事前に上長の承認を得ているか確認してください
* ユーザーに詳細の確認は不要です。承認の有無だけ確認してください
* 承認を得ていない場合は、先に上長の承認を取得するよう案内してください

3. 業務目的チェック
- すべての申請について業務関連性を確認してください
* 業務目的が不明確な場合は、詳細な目的をユーザーに確認してください
* 業務目的と判断できない場合は申請を受け付けないでください
"""
```

### 2. プロンプト生成関数の修正

既存のプロンプト生成関数を修正し、外部ルールを読み込むようにします。

```python
# prompt/prompt_travel.py の修正後
from datetime import datetime, timedelta
from agent_knowledge.travel_policies import get_travel_rules

def _get_travel_system_prompt() -> str:
    """現在日付を含むシステムプロンプトを動的に生成"""
    today = datetime.now()
    three_months_ago = today - timedelta(days=90)
    
    # 日付文字列を作成
    today_str = today.strftime('%Y-%m-%d')
    three_months_ago_str = three_months_ago.strftime('%Y-%m-%d')
    
    # 外部ルールを読み込む
    rules_text = get_travel_rules(today_str, three_months_ago_str)
    
    # プロンプトを構築
    return f"""
    あなたは交通費精算申請エージェントです。
    ユーザーから移動情報を一区間ずつ収集し、交通費を計算して申請書を作成します。

    ## 現在の日付情報
    - 今日の日付: {today.strftime('%Y年%m月%d日')} ({today_str})
    - 3ヶ月前の日付: {three_months_ago.strftime('%Y年%m月%d日')} ({three_months_ago_str})
    - 申請可能な最古の日付: {three_months_ago_str}
    - **重要**: 日付が {three_months_ago_str} ～{today_str}の範囲であれば、過去3ヶ月以内として申請可能です

    ## 役割
    1. 交通費の算出処理
    - calculate_fareツールを利用して、dataフォルダ内の各交通手段の経路間の費用を確認して、交通費を計算する

    2. Excel申請書の生成
    - travel_excel_generatorツールで申請書を生成

    {rules_text}
    
    ## 処理フロー
    1. ユーザーから一区間の移動情報（出発地、目的地、日付、交通手段）を収集する
    2. calculate_fareツールで各交通手段ごとに各経路間の交通費を計算する
       ※ユーザーが「渋谷駅」のように「駅」を含めて入力した場合は、「駅」を含めず経路情報を収集してください。
    3. 区間ごとに「交通費申請ルール」に基づいてチェックする
    3. 計算結果を区間ごとにユーザーに確認する
    4. 次の区間の有無を必ず確認して、ある場合は次の区間も計算をする
    5. travel_excel_generatorツールを実行する

    ## 重要な注意事項
    - 各区間の情報を収集する際は、出発地、目的地、日付、交通手段の４項目を確認してください
    - 交通手段は「電車」「バス」「タクシー」「飛行機」のいずれかです
    - 可能な限り、calculate_fareツールで交通費を計算してください
    - 必ず一区間ずつ処理してください。
    - 必ず「交通費申請ルール」のチェックをすべて行ってください
    - 修正依頼があった場合は、dataフォルダを再度読み込み、対象区間の交通費を再計算してください。

    ## エラーハンドリング
    エージェント起動時のエラーやツール使用時のエラーメッセージは、
    申請受付窓口エージェントにわかりやすく要約して伝えてください
    その際エラーの原因と対処方法を明確に伝えて、処理を停止するように伝えてください

    常に丁寧で分かりやすい日本語で対話してください
    """
```

```python
# prompt/prompt_receipt.py の修正後
from datetime import datetime, timedelta
from agent_knowledge.receipt_policies import get_receipt_rules

def _get_receipt_expense_system_prompt() -> str:
    """現在日付を含むシステムプロンプトを動的に生成"""
    today = datetime.now()
    three_months_ago = today - timedelta(days=90)
    
    # 日付文字列を作成
    today_str = today.strftime('%Y-%m-%d')
    three_months_ago_str = three_months_ago.strftime('%Y-%m-%d')
    
    # 外部ルールを読み込む
    rules_text = get_receipt_rules(today_str, three_months_ago_str)
    
    return f"""
    あなたは経費精算申請エージェントです。
    image_readerツールを利用して経費申請情報を収集して、申請書を作成します。

    ## 現在の日付情報
    - 今日の日付: {today.strftime('%Y年%m月%d日')} ({today_str})
    - 3ヶ月前の日付: {three_months_ago.strftime('%Y年%m月%d日')} ({three_months_ago_str})
    - 申請可能な最古の日付: {three_months_ago_str}
    - **重要**: 領収書の日付が {three_months_ago_str} ～{today_str}の範囲であれば、過去3ヶ月以内として申請可能です

    ## 役割
    1. 領収書画像の処理
        -image_readerツールで画像から情報を抽出（店舗名、金額、日付、品目）

    2. 経費区分の判断
        -品目を分析して適切な経費区分を判断：
            * 事務用品費: 書籍、文房具、オフィス用品など
            * 宿泊費: ホテル、宿泊施設など
            * 資格精算費: 資格試験、受験料、認定費用など
            * その他経費: 上記以外

    3. Excel申請書の生成
        - receipt_excel_generatorツールで申請書を生成
        - 申請者名と申請日は自動的に取得されます（引数として渡す必要はありません）

    {rules_text}

    ## 処理フロー
    1. ユーザーから領収書画像のパスを収集する
    2. image_readerツールで画像から情報を抽出する
    3. 抽出した情報をユーザーに確認する
    4. 申請内容に対して、「経費申請ルール」に基づいて３つのチェック項目を必ず行う
    5. receipt_excel_generatorツールを実行する
    
    ## 重要な注意事項
    - 領収書画像のパスは必ず確認してください
    - 抽出した情報は必ずユーザーに確認してください
    -「経費申請ルール」のチェックは３つすべて必ず行ってください
    - 修正依頼があった場合は対象の区間を再計算してください。

    ## エラーハンドリング
    エージェント起動時のエラーやツール使用時のエラーメッセージは、
    申請受付窓口エージェントにわかりやすく要約して伝えてください
    その際エラーの原因と対処方法を明確に伝えて、処理を停止するように伝えてください

    常に丁寧で分かりやすい日本語で対話してください
    """
```

## データモデル

### ルール関数のシグネチャ

```python
from typing import Callable

# ルール取得関数の型
RuleGetter = Callable[[str, str], str]

# 各ポリシーファイルは以下のシグネチャの関数を提供する
def get_travel_rules(today: str, three_months_ago: str) -> str:
    """交通費申請ルールテキストを取得"""
    pass

def get_receipt_rules(today: str, three_months_ago: str) -> str:
    """経費申請ルールテキストを取得"""
    pass
```

## 正確性プロパティ

*プロパティとは、システムのすべての有効な実行において真であるべき特性や動作のことです。プロパティは、人間が読める仕様と機械で検証可能な正確性保証の橋渡しとなります。*

### プロパティ1: ルール関数の存在

*すべての*ポリシーファイル（travel_policies.py、receipt_policies.py）に対して、get_{type}_rules関数が存在し、2つの文字列引数を受け取り、文字列を返すべきである

**検証: 要件 1.1, 1.2**

### プロパティ2: ルールテキストの完全性

*すべての*ルール取得関数に対して、返されるテキストには「日付チェック」と「金額チェック」のセクションが含まれるべきである

**検証: 要件 1.3, 1.4**

### プロパティ3: 日付の動的注入

*すべての*ルール取得関数に対して、引数として渡された日付文字列（today、three_months_ago）が返されるテキストに含まれるべきである

**検証: 要件 2.1, 2.2**

### プロパティ4: プロンプト生成時のルール読み込み

*すべての*プロンプト生成関数に対して、実行時にポリシーファイルからルール取得関数をインポートし、生成されたプロンプトテキストにルールの内容が含まれるべきである

**検証: 要件 3.1, 3.2**

### プロパティ5: プロンプト構造の保持

*すべての*プロンプト生成関数に対して、外部ルールを使用して生成されたプロンプトは、元の埋め込みバージョンと同じセクション構造（役割、ルール、処理フロー、注意事項、エラーハンドリング）を持つべきである

**検証: 要件 3.3, 4.1**

### プロパティ6: 日付計算ロジックの保持

*すべての*プロンプト生成関数に対して、today と three_months_ago の計算結果が、リファクタリング前と同じ値（datetime.now() と datetime.now() - timedelta(days=90)）であるべきである

**検証: 要件 4.4**

### プロパティ7: ルールテキストの一致

*すべての*ポリシータイプ（travel、receipt）に対して、外部ファイルから読み込んだルールテキストは、元のプロンプトに埋め込まれていたルールテキストと内容が一致するべきである

**検証: 要件 4.1, 4.5**

## エラーハンドリング

### エラーの種類と対応

1. **ImportError**: ポリシーファイルまたはルール関数が見つからない場合
   - エラーメッセージ: "ポリシーファイル 'agent_knowledge.{policy_name}_policies' が見つかりません。"
   - 対応: ファイルパスを確認し、ファイルが存在することを確認する

2. **AttributeError**: ルール取得関数が定義されていない場合
   - エラーメッセージ: "ポリシーファイル '{policy_name}_policies.py' に 'get_{policy_name}_rules' 関数が定義されていません。"
   - 対応: ポリシーファイルに正しい関数名で関数を定義する

3. **TypeError**: ルール取得関数の引数が不正な場合
   - エラーメッセージ: "ルール取得関数の引数が不正です。2つの文字列引数（today、three_months_ago）が必要です。"
   - 対応: 関数のシグネチャを確認する

### エラーハンドリングの実装

```python
# prompt/prompt_travel.py のエラーハンドリング例
from datetime import datetime, timedelta

def _get_travel_system_prompt() -> str:
    """現在日付を含むシステムプロンプトを動的に生成"""
    today = datetime.now()
    three_months_ago = today - timedelta(days=90)
    
    today_str = today.strftime('%Y-%m-%d')
    three_months_ago_str = three_months_ago.strftime('%Y-%m-%d')
    
    try:
        from agent_knowledge.travel_policies import get_travel_rules
        rules_text = get_travel_rules(today_str, three_months_ago_str)
    except ImportError as e:
        raise ImportError(
            "ポリシーファイル 'agent_knowledge.travel_policies' が見つかりません。"
            "agent_knowledge/travel_policies.py を確認してください。"
        ) from e
    except AttributeError as e:
        raise AttributeError(
            "ポリシーファイル 'travel_policies.py' に 'get_travel_rules' 関数が定義されていません。"
        ) from e
    except TypeError as e:
        raise TypeError(
            "ルール取得関数の引数が不正です。2つの文字列引数（today、three_months_ago）が必要です。"
        ) from e
    
    # プロンプトを構築...
```

## テスト戦略

### デュアルテストアプローチ

このシステムでは、ユニットテストとプロパティベーステストの両方を使用します：

- **ユニットテスト**: 特定の例、エッジケース、エラー条件を検証
- **プロパティテスト**: すべての入力に対する普遍的なプロパティを検証

両方のアプローチは補完的であり、包括的なカバレッジに必要です。

### ユニットテストのバランス

ユニットテストは特定の例とエッジケースに焦点を当てます：

- ポリシーファイルの存在確認
- ルール取得関数の存在確認
- 特定のエラーケース（ファイル未検出、関数未定義）
- 統合ポイント（プロンプト生成関数とポリシーファイルの連携）

プロパティテストは以下に焦点を当てます：

- すべてのポリシーファイルに対するルール関数の検証
- すべてのルールテキストに対する構造検証
- すべてのプロンプト生成関数に対するルール注入検証
- ランダム化による包括的な入力カバレッジ

### プロパティベーステストの設定

- **テストライブラリ**: Hypothesis（Python用プロパティベーステストライブラリ）
- **最小イテレーション数**: 100回（ランダム化のため）
- **タグ形式**: **Feature: agent-knowledge-externalization, Property {番号}: {プロパティテキスト}**

各正確性プロパティは、単一のプロパティベーステストによって実装される必要があります。

### テストケースの例

#### ユニットテスト例

```python
# tests/test_policy_files.py

def test_travel_policy_file_exists():
    """交通費ポリシーファイルが存在することを確認"""
    from agent_knowledge.travel_policies import get_travel_rules
    assert callable(get_travel_rules)

def test_receipt_policy_file_exists():
    """経費ポリシーファイルが存在することを確認"""
    from agent_knowledge.receipt_policies import get_receipt_rules
    assert callable(get_receipt_rules)

def test_travel_rules_contain_required_sections():
    """交通費ルールに必要なセクションが含まれることを確認"""
    from agent_knowledge.travel_policies import get_travel_rules
    rules = get_travel_rules('2024-02-01', '2023-11-01')
    assert '日付チェック' in rules
    assert '金額チェック' in rules
    assert '10,000円' in rules

def test_receipt_rules_contain_required_sections():
    """経費ルールに必要なセクションが含まれることを確認"""
    from agent_knowledge.receipt_policies import get_receipt_rules
    rules = get_receipt_rules('2024-02-01', '2023-11-01')
    assert '日付チェック' in rules
    assert '金額チェック' in rules
    assert '業務目的チェック' in rules
    assert '5,000円' in rules

def test_import_error_handling():
    """存在しないポリシーファイルのインポートでエラーが発生することを確認"""
    with pytest.raises(ImportError):
        from agent_knowledge.nonexistent_policies import get_nonexistent_rules
```

#### プロパティテスト例

```python
# tests/test_policy_properties.py
from hypothesis import given, strategies as st
from datetime import datetime, timedelta

# Feature: agent-knowledge-externalization, Property 2: ルールテキストの完全性
@given(
    today=st.dates(min_value=datetime(2020, 1, 1).date(), max_value=datetime(2030, 12, 31).date()),
    days_ago=st.integers(min_value=1, max_value=365)
)
def test_rule_text_completeness(today, days_ago):
    """すべてのルール取得関数が必要なセクションを含むことを確認"""
    from agent_knowledge.travel_policies import get_travel_rules
    from agent_knowledge.receipt_policies import get_receipt_rules
    
    three_months_ago = today - timedelta(days=days_ago)
    today_str = today.strftime('%Y-%m-%d')
    three_months_ago_str = three_months_ago.strftime('%Y-%m-%d')
    
    # 交通費ルール
    travel_rules = get_travel_rules(today_str, three_months_ago_str)
    assert '日付チェック' in travel_rules
    assert '金額チェック' in travel_rules
    
    # 経費ルール
    receipt_rules = get_receipt_rules(today_str, three_months_ago_str)
    assert '日付チェック' in receipt_rules
    assert '金額チェック' in receipt_rules
    assert '業務目的チェック' in receipt_rules

# Feature: agent-knowledge-externalization, Property 3: 日付の動的注入
@given(
    today=st.dates(min_value=datetime(2020, 1, 1).date(), max_value=datetime(2030, 12, 31).date()),
    days_ago=st.integers(min_value=1, max_value=365)
)
def test_date_injection(today, days_ago):
    """すべてのルール取得関数が引数の日付を含むことを確認"""
    from agent_knowledge.travel_policies import get_travel_rules
    from agent_knowledge.receipt_policies import get_receipt_rules
    
    three_months_ago = today - timedelta(days=days_ago)
    today_str = today.strftime('%Y-%m-%d')
    three_months_ago_str = three_months_ago.strftime('%Y-%m-%d')
    
    # 交通費ルール
    travel_rules = get_travel_rules(today_str, three_months_ago_str)
    assert today_str in travel_rules
    assert three_months_ago_str in travel_rules
    
    # 経費ルール
    receipt_rules = get_receipt_rules(today_str, three_months_ago_str)
    assert today_str in receipt_rules
    assert three_months_ago_str in receipt_rules
```

### 統合テスト

```python
# tests/test_prompt_integration.py

def test_travel_prompt_generation_with_external_rules():
    """交通費プロンプト生成が外部ルールを使用することを確認"""
    from prompt.prompt_travel import _get_travel_system_prompt
    
    prompt = _get_travel_system_prompt()
    
    # プロンプトにルールの内容が含まれることを確認
    assert '交通費申請ルール' in prompt
    assert '日付チェック' in prompt
    assert '金額チェック' in prompt
    assert '10,000円' in prompt
    assert '処理フロー' in prompt

def test_receipt_prompt_generation_with_external_rules():
    """経費プロンプト生成が外部ルールを使用することを確認"""
    from prompt.prompt_receipt import _get_receipt_expense_system_prompt
    
    prompt = _get_receipt_expense_system_prompt()
    
    # プロンプトにルールの内容が含まれることを確認
    assert '経費申請ルール' in prompt
    assert '日付チェック' in prompt
    assert '金額チェック' in prompt
    assert '業務目的チェック' in prompt
    assert '5,000円' in prompt
    assert '処理フロー' in prompt

def test_prompt_structure_preservation():
    """プロンプト構造が保持されることを確認"""
    from prompt.prompt_travel import _get_travel_system_prompt
    
    prompt = _get_travel_system_prompt()
    
    # 必要なセクションが存在することを確認
    assert '役割' in prompt
    assert '交通費申請ルール' in prompt
    assert '処理フロー' in prompt
    assert '重要な注意事項' in prompt
    assert 'エラーハンドリング' in prompt
```

## 実装の注意事項

### 1. ポリシーファイルの配置

- agent_knowledgeフォルダをプロジェクトルートに作成
- __init__.pyを作成してPythonパッケージとして認識させる
- 各ポリシーファイルは独立したモジュールとして作成

### 2. インポートパスの管理

- 相対インポートではなく絶対インポートを使用
- `from agent_knowledge.travel_policies import get_travel_rules`
- `from agent_knowledge.receipt_policies import get_receipt_rules`

### 3. 後方互換性の確保

- プロンプトの内容が変わらないことを確認するため、既存のプロンプトと新しいプロンプトを比較するテストを実装
- 日付計算ロジックは変更しない（datetime.now()とtimedelta(days=90)を使用）
- ルールテキストの文言も可能な限り保持

### 4. エラーメッセージの明確化

- ユーザーがエラーを理解しやすいように、日本語で明確なエラーメッセージを提供
- エラーメッセージには、問題の原因と解決方法を含める
- ファイルパスや関数名を具体的に示す

## マイグレーション計画

### フェーズ1: ポリシーファイルの作成

1. agent_knowledgeフォルダを作成
2. __init__.pyを作成
3. travel_policies.pyを作成し、get_travel_rules関数を実装
4. receipt_policies.pyを作成し、get_receipt_rules関数を実装

### フェーズ2: プロンプト生成関数の修正

1. prompt_travel.pyを修正し、外部ルールを読み込むように変更
2. prompt_receipt.pyを修正し、外部ルールを読み込むように変更
3. 既存のプロンプトと新しいプロンプトを比較し、内容が同じことを確認

### フェーズ3: テストの実装

1. ユニットテストを実装（ポリシーファイル、プロンプト生成）
2. プロパティテストを実装（ルールテキスト検証、日付注入）
3. 統合テストを実装（エージェント実行）

### フェーズ4: 検証とデプロイ

1. すべてのテストが通ることを確認
2. エージェントを実行し、動作が変わらないことを確認
3. ドキュメントを更新

## 今後の拡張性

### 新しいポリシーの追加

新しいエージェントや申請タイプを追加する場合：

1. agent_knowledge/{new_type}_policies.pyを作成
2. get_{new_type}_rules関数を定義
3. プロンプト生成関数で関数を呼び出す
4. テストを追加

### ルールの動的更新

将来的に、ルールを動的に更新する機能を追加する場合：

1. ポリシーファイルをJSONまたはYAMLに変更
2. 管理画面からルールを編集できるようにする
3. ルール変更履歴を記録
