"""交通費精算申請エージェント"""
from strands import Agent, tool, ToolContext
from strands import ModelRetryStrategy
from strands.agent.conversation_manager import SlidingWindowConversationManager
from tools.fare_tools import load_fare_data, calculate_fare
from tools.excel_generator import travel_excel_generator
from session.session_manager import SessionManagerFactory
from handlers.human_approval_hook import HumanApprovalHook
from prompt.prompt_travel import _get_travel_system_prompt
from handlers.loop_control_hook import LoopControlHook


# グローバル変数
travel_agent_instance = None
_session_manager = None


#エージェントの初期化
def _get_travel_agent(session_id: str = None) -> Agent:
    """
    交通費精算申請エージェントのインスタンスを取得
    （シングルトンパターン）
    
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
        
        # セッションマネージャーの作成
        # （session_idが指定されている場合）
        if session_id:
            _session_manager = (
                SessionManagerFactory.create_session_manager(session_id)
            )
        
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
            system_prompt=_get_travel_system_prompt(),#別モジュールから取得
            tools=[
                calculate_fare,
                travel_excel_generator
            ],
            conversation_manager=SlidingWindowConversationManager(
                window_size=20,
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

