"""交通費精算申請エージェント"""
from strands import Agent, tool
from strands.agent.conversation_manager import SlidingWindowConversationManager
from tools.fare_tools import load_fare_data, calculate_fare
from tools.validation_tools import validate_input
from tools.report_tools import generate_report


# システムプロンプト
TRAVEL_SYSTEM_PROMPT = """あなたは交通費精算申請エージェントです。
ユーザーから移動情報を一区間ずつ収集し、交通費を計算して申請書を作成します。

処理フロー:
1. ユーザーから一区間の移動情報（出発地、目的地、日付、交通手段）を収集
2. calculate_fareツールで交通費を計算
3. 計算結果をユーザーに確認
4. 次の区間の有無を確認
5. すべての区間の入力完了後、最終確認
6. 申請書形式(PDF/JSON)を質問
7. generate_reportツールで申請書を生成・保存

重要な注意事項:
- 必ず一区間ずつ処理してください
- 各区間の情報を収集する際は、出発地、目的地、日付、交通手段のすべてを確認してください
- 交通手段は「train」「bus」「taxi」「airplane」のいずれかです
- 計算結果は必ずユーザーに確認してください
- すべての区間の入力が完了したら、最終確認を行ってください
- 申請書の形式は必ずユーザーに選択してもらってください(PDFまたはJSON)

generate_reportツールの使用方法:
- routesパラメータ: 収集した全経路データのリスト（必須）
- formatパラメータ: "pdf" または "json"（必須）
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
            system_prompt=TRAVEL_SYSTEM_PROMPT,
            tools=[
                calculate_fare,
                validate_input,
                generate_report
            ],
            conversation_manager=SlidingWindowConversationManager(),
            agent_id="travel_agent",
            name="交通費精算申請エージェント",
            description="ユーザーから移動情報を収集し、交通費を計算して申請書を作成します",
            callback_handler=None  # ストリーミング出力を無効化
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
        
        # エージェント実行
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
    global travel_agent_instance
    travel_agent_instance = None
