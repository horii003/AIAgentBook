"""交通費精算申請エージェント"""
from datetime import datetime, timedelta
from strands import Agent, tool, ToolContext
from strands import ModelRetryStrategy
from strands.agent.conversation_manager import SlidingWindowConversationManager
from tools.fare_tools import load_fare_data, calculate_fare
from tools.excel_generator import travel_excel_generator
from session.session_manager import SessionManagerFactory
from handlers.human_approval_hook import HumanApprovalHook
from handlers.loop_control_hook import LoopControlHook

def _get_travel_system_prompt() -> str:

    """現在日付を含むシステムプロンプトを動的に生成"""
    today = datetime.now()
    three_months_ago = today - timedelta(days=90)


    return f"""
    
    あなたは交通費精算申請エージェントです。
    ユーザーから移動情報を一区間ずつ収集し、交通費を計算して申請書を作成します。

    ## 現在の日付情報
    - 今日の日付: {today.strftime('%Y年%m月%d日')} ({today.strftime('%Y-%m-%d')})
    - 3ヶ月前の日付: {three_months_ago.strftime('%Y年%m月%d日')} ({three_months_ago.strftime('%Y-%m-%d')})
    - 申請可能な最古の日付: {three_months_ago.strftime('%Y-%m-%d')}
    - **重要**: 日付が {three_months_ago.strftime('%Y-%m-%d')} ～{today.strftime('%Y-%m-%d')}の範囲であれば、過去3ヶ月以内として申請可能です

    ## 役割
    1. 交通費の算出処理
    calculate_fareツールで交通費を計算

    2. Excel申請書の生成
    travel_excel_generatorツールで申請書を生成


    ## 交通費申請ルール（必須チェック項目）
    1. 日付チェック
    - 日付が {three_months_ago.strftime('%Y-%m-%d')} より前（3ヶ月を超える）の場合：
    * まず、ユーザーに日付の確認と修正を提案してください
    * 修正されない場合は、業務上の正当な理由を確認してください
    * 正当な理由がない場合は申請を受け付けないでください

    - 日付が {three_months_ago.strftime('%Y-%m-%d')} ～{today.strftime('%Y-%m-%d')}の範囲である場合：
    * 日付チェックは問題ありません（次のステップに進んでください）

    2. 金額チェック
    - 50,00円を超える申請の場合：
    * 必ず事前に上長の承認を得ているか確認してください
    * ユーザーに会話の深堀は不要です。承認の有無だけ確認してください。
    * 承認を得ていない場合は、先に上長の承認を取得するよう案内してください
    

    ## 処理フロー
    1. ユーザーから一区間の移動情報（出発地、目的地、日付、交通手段）を収集
    2. calculate_fareツールで交通費を計算
    3. 計算結果をユーザーに確認
    4. 次の区間の有無を確認
    5. 交通費申請ルールに基づいてチェック
    6. すべての区間の入力完了後、申請内容をまとめて表示してユーザーに最終確認をしてください。
    7. ユーザーから修正要望があれば、区間を確認して、修正を受け付けて再度交通費を計算してください。
    9. すべての情報が揃い、ルールチェックが完了したら、travel_excel_generatorツールを実行してください

    ## 重要な注意事項
    - 必ず一区間ずつ処理してください
    - 各区間の情報を収集する際は、出発地、目的地、日付、交通手段のすべてを確認してください
    - 交通手段は「train」「bus」「taxi」「airplane」のいずれかです
    - 可能な限り、calculate_fareツールで交通費を計算してください
    - 計算結果は必ずユーザーに確認してください

   
    ## travel_excel_generatorツールの使用方法
    - routesパラメータ: 収集した全経路データのリスト（必須）
    - 申請者名は自動的に取得されます（引数として渡す必要はありません）
    - エラーが発生した場合は、ツールの戻り値のmessageフィールドを確認してください
    - ツールの実行結果に「キャンセルしました」というメッセージが含まれている場合は、ユーザーの指示に従ってください

    常に丁寧で分かりやすい日本語で対話してください。
    """

# グローバル変数
travel_agent_instance = None
_session_manager = None


#エージェントの初期化
def _get_travel_agent(session_id: str = None) -> Agent:
    """
    交通費精算申請エージェントのインスタンスを取得（シングルトンパターン）
    
    Args:
        session_id: セッションID（省略時はセッション管理なし）
    
    Returns:
        Agent: 交通費精算申請エージェントのインスタンス
    """

    global travel_agent_instance, _session_manager
    
    if travel_agent_instance is None:
        # 運賃データの事前読み込み
        try:
            load_fare_data()
        except Exception as e:
            raise RuntimeError(f"運賃データの読み込みに失敗しました: {e}")
        
        # セッションマネージャーの作成（session_idが指定されている場合）
        if session_id:
            _session_manager = SessionManagerFactory.create_session_manager(session_id)
        
        # Human-in-the-Loop承認フックの作成
        approval_hook = HumanApprovalHook()
        
        # ループ制御フックの作成
        loop_control_hook = LoopControlHook(
            max_iterations=10,  # 専門エージェントは特定タスクに集中するため標準的な回数
            agent_name="交通費精算申請エージェント"
        )
        
        # エージェントの初期化
        travel_agent_instance = Agent(
            model="jp.anthropic.claude-sonnet-4-5-20250929-v1:0",
            system_prompt=_get_travel_system_prompt(),
            tools=[
                calculate_fare,
                travel_excel_generator
            ],
            conversation_manager=SlidingWindowConversationManager(
                window_size=20,  # 複数区間の情報を保持する必要があるため中程度
                should_truncate_results=True,
                per_turn=False
            ),
            agent_id="travel_agent",
            name="交通費精算申請エージェント",
            description="ユーザーから移動情報を収集し、交通費を計算して申請書を作成します",
            callback_handler=None,  # ストリーミング出力を無効化
            retry_strategy=ModelRetryStrategy(
                max_attempts=6,
                initial_delay=4,
                max_delay=240
            ),
            session_manager=_session_manager,  # セッションマネージャーを設定
            hooks=[approval_hook, loop_control_hook]  # Human-in-the-Loop承認フックとループ制御フックを追加
        )
    
    return travel_agent_instance

#Agent as Tools
@tool(context=True)
def travel_agent(query: str, tool_context: ToolContext) -> str:
    """
    交通費精算申請ツール
    
    ユーザーから移動情報を一区間ずつ収集し、交通費を計算して申請書を作成します。
    会話履歴を保持して、複数回の呼び出しでも段階的に情報を収集します。
    
    Args:
        query: ユーザーからの入力や質問
    
    Returns:
        str: エージェントからの応答
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.info("[travel_agent] ツールが呼び出されました")

    try:
        # invocation_stateからsession_idを取得
        session_id = None
        if tool_context and tool_context.invocation_state:
            session_id = tool_context.invocation_state.get("session_id")
        
        # エージェントインスタンスを取得（初回は初期化、2回目以降は既存インスタンスを使用する）
        agent = _get_travel_agent(session_id=session_id)
        
        # invocation_stateから申請者名と申請日を取得
        applicant_name = None
        application_date = None
        if tool_context and tool_context.invocation_state:
            applicant_name = tool_context.invocation_state.get("applicant_name")
            application_date = tool_context.invocation_state.get("application_date")
        
        # 通常の実行（invocation_stateを渡す）
        if applicant_name:
            invocation_state = {"applicant_name": applicant_name}
            if application_date:
                invocation_state["application_date"] = application_date
            
            response = agent(
                query, 
                invocation_state=invocation_state
            )
        else:
            response = agent(query)
        
        return str(response)
    
    except RuntimeError as e:
        # ループ制限エラーの処理
        if "エージェントループの制限" in str(e):
            # ログ記録なし（詳細はloop_control_hookで記録済み）
            error_msg = (
                "申し訳ございません。処理が複雑すぎて完了できませんでした。\n\n"
                "以下のいずれかをお試しください：\n"
                "1. 経路を1つずつ申請してください\n"
                "2. より具体的な情報（日付、出発地、目的地、交通手段）を提供してください\n"
                "3. 不要な情報を削除してください\n\n"
                "受付窓口に戻りますので、もう一度シンプルな内容でお試しください。"
            )
            logger.info(f"[travel_agent] ループ制限エラーメッセージを返却: {error_msg[:50]}...")
            return error_msg
        else:
            logger.warning(f"[travel_agent] 予期しないRuntimeError: {str(e)[:100]}")
            return f"エラーが発生しました。受付窓口に戻ります。"
    
    except Exception as e:
        logger.error(f"[travel_agent] エラーが発生しました: {e}")
        return f"エラーが発生しました。受付窓口に戻ります。"


#エージェントのリセット
def reset_travel_agent():
    """
    交通費精算申請エージェントの状態をリセット
    
    ユーザーから会話をリセットしたい要望があった場合は、会話履歴をクリアする。
    """
    global travel_agent_instance, _session_manager
    travel_agent_instance = None
    _session_manager = None

