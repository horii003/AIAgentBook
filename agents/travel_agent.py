"""交通費精算申請エージェント"""
from datetime import datetime, timedelta
from strands import Agent, tool
from strands import ModelRetryStrategy
from strands.agent.conversation_manager import SlidingWindowConversationManager
from tools.fare_tools import load_fare_data, calculate_fare
from tools.validation_tools import validate_input
from tools.excel_generator import travel_excel_generator

def _get_travel_system_prompt() -> str:
    """現在日付を含むシステムプロンプトを動的に生成"""
    today = datetime.now()
    three_months_ago = today - timedelta(days=90)


    return f"""あなたは交通費精算申請エージェントです。
ユーザーから移動情報を一区間ずつ収集し、交通費を計算して申請書を作成します。

## 現在の日付情報
- 今日の日付: {today.strftime('%Y年%m月%d日')} ({today.strftime('%Y-%m-%d')})
- 3ヶ月前の日付: {three_months_ago.strftime('%Y年%m月%d日')} ({three_months_ago.strftime('%Y-%m-%d')})
- 申請可能な最古の日付: {three_months_ago.strftime('%Y-%m-%d')}
- **重要**: 日付が {three_months_ago.strftime('%Y-%m-%d')} ～{today.strftime('%Y-%m-%d')}の範囲であれば、過去3ヶ月以内として申請可能です

## 役割

1. **交通費の算出処理**
   - calculate_fareツールで交通費を計算

2. **Excel申請書の生成**
   - travel_excel_generatorツールで申請書を生成
   - 金額が30,000円を超える場合はエラーを返す

## 交通費申請ルール（必須チェック項目）

### 1. 日付チェック
- 日付が {three_months_ago.strftime('%Y-%m-%d')} より前（3ヶ月を超える）の場合：
  * まず、ユーザーに日付の確認と修正を提案してください
  * 修正されない場合は、業務上の正当な理由を確認してください
  * 正当な理由がない場合は申請を受け付けないでください
- 日付が {three_months_ago.strftime('%Y-%m-%d')} ～{today.strftime('%Y-%m-%d')}の範囲である場合：
  * 日付チェックは問題ありません（次のステップに進んでください）

### 2. 金額チェック
- 5,000円を超える申請の場合：
  * 必ず事前に上長の承認を得ているか確認してください
  * 承認を得ていない場合は、先に上長の承認を取得するよう案内してください
- 30,000円を超える申請：
  * システムの制限により受け付けられません
  * エラーメッセージを表示してください

### 3. 業務目的チェック
- すべての申請について業務関連性を確認してください
- 業務目的が不明確な場合：
  * 詳細な目的をユーザーに確認してください
  * 特に5,000円以上の高額申請の場合は、より詳細な確認が必要です
  * 業務目的と判断できない場合は申請を受け付けないでください

### 4. 通勤定期重複チェック
- 以下の経路は通勤経路として取り扱い、通勤定期の区間とする
  * 上野駅～豊洲駅
  * 目黒駅～豊洲駅
  * 川崎駅～豊洲駅
- 申請区間が通勤定期区間と重複する場合、申請を受け付けないでください

## 処理フロー
1. ユーザーから一区間の移動情報（出発地、目的地、日付、交通手段）を収集
2. calculate_fareツールで交通費を計算
3. 計算結果をユーザーに確認
4. 次の区間の有無を確認
5. **交通費申請ルールに基づいてチェック**：
   - 日付が {three_months_ago.strftime('%Y-%m-%d')} 以降か確認
   - 5,000円超の場合は上長承認を確認
   - 業務目的を確認
6. すべての区間の入力完了後、最終確認
7. **交通費申請ルールに基づいてチェック**：
   - 申請全体についてチェックする
   - 合計金額が5,000円超の場合は上長承認を確認
   - 業務目的を確認
8. 必要に応じて修正を受け付ける
9. travel_excel_generatorツールで申請書を生成・保存

## 重要な注意事項
- 必ず一区間ずつ処理してください
- 各区間の情報を収集する際は、出発地、目的地、日付、交通手段のすべてを確認してください
- 交通手段は「train」「bus」「taxi」「airplane」のいずれかです
- 計算結果は必ずユーザーに確認してください
- すべての区間の入力が完了したら、最終確認を行ってください
  
## travel_excel_generatorツールの使用方法:
- routesパラメータ: 収集した全経路データのリスト（必須）
- user_idパラメータ: "0001"（デフォルト値を使用）
- ツールは1回だけ呼び出してください
- エラーが発生した場合は、ツールの戻り値のmessageフィールドを確認してください
- successフィールドがtrueの場合のみ成功です

常に丁寧で分かりやすい日本語で対話してください。
"""
# グローバル変数
travel_agent_instance = None

#エージェントの初期化
def _get_travel_agent() -> Agent:
    """
    交通費精算申請エージェントのインスタンスを取得（シングルトンパターン）
    
    Returns:
        Agent: 交通費精算申請エージェントのインスタンス
    """

    global travel_agent_instance
    
    if travel_agent_instance is None:
        # 運賃データの事前読み込み
        try:
            load_fare_data()
        except Exception as e:
            raise RuntimeError(f"運賃データの読み込みに失敗しました: {e}")
        
        # エージェントの初期化
        travel_agent_instance = Agent(
            model="jp.anthropic.claude-sonnet-4-5-20250929-v1:0",
            system_prompt=_get_travel_system_prompt(),
            tools=[
                calculate_fare,
                # validate_input,
                travel_excel_generator
            ],
            conversation_manager=SlidingWindowConversationManager(),
            agent_id="travel_agent",
            name="交通費精算申請エージェント",
            description="ユーザーから移動情報を収集し、交通費を計算して申請書を作成します",
            callback_handler=None,  # ストリーミング出力を無効化
            retry_strategy=ModelRetryStrategy(
                max_attempts=6,
                initial_delay=4,
                max_delay=240
            )
        )
    
    return travel_agent_instance

#Agent as Tools
@tool
def travel_agent(query: str) -> str:
    """
    交通費精算申請ツール
    
    ユーザーから移動情報を一区間ずつ収集し、交通費を計算して申請書を作成します。
    会話履歴を保持して、複数回の呼び出しでも段階的に情報を収集します。
    
    Args:
        query: ユーザーからの入力や質問
    
    Returns:
        str: エージェントからの応答
    """    
    try:
        # エージェントインスタンスを取得（初回は初期化、2回目以降は既存インスタンスを使用する）
        agent = _get_travel_agent()

        response = agent(query)

        return str(response)
    
    except Exception as e:
        return f"エラーが発生しました: {e}"


#エージェントのリセット
def reset_travel_agent():
    """
    交通費精算申請エージェントの状態をリセット
    
    ユーザーから会話をリセットしたい要望があった場合は、会話履歴をクリアする。
    """
    global travel_agent_instance, travel_agent_interrupt_state
    travel_agent_instance = None

