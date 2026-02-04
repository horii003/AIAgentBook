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
from models.data_models import InvocationState
from pydantic import ValidationError


#エージェントの初期化
def _get_travel_agent(session_id: str) -> Agent:
    """
    交通費精算申請エージェントのインスタンスを作成
    
    Args:
        session_id: セッションID（必須）
    
    Returns:
        Agent: 交通費精算申請エージェントのインスタンス
    """
    # 運賃データの事前読み込み
    try:
        load_fare_data()
    except Exception as e:
        raise RuntimeError(f"運賃データの読み込みに失敗しました: {e}")
    
    # セッションマネージャーの作成
    session_manager = SessionManagerFactory.create_session_manager(session_id)
    
    # Human-in-the-Loop承認フックの作成
    approval_hook = HumanApprovalHook()
    
    # ループ制御フックの作成
    loop_control_hook = LoopControlHook(
        max_iterations=10,  # 専門エージェントは特定タスクに集中するため標準的な回数
        agent_name="交通費精算申請エージェント"
    )
    
    # エージェントの初期化
    agent = Agent(
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
        session_manager=session_manager,  # セッションマネージャーを設定
        hooks=[approval_hook, loop_control_hook]  # Human-in-the-Loop承認フックとループ制御フックを追加
    )
    
    return agent

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
        # invocation_stateのバリデーション
        if not tool_context or not tool_context.invocation_state:
            logger.warning("[travel_agent] invocation_stateが存在しません")
            return "申請者情報が設定されていません。受付窓口に戻ります。"
        
        try:
            state = InvocationState(**tool_context.invocation_state)
        except ValidationError as e:
            logger.error(f"[travel_agent] invocation_stateのバリデーションエラー: {e}")
            error_messages = []
            for error in e.errors():
                field = ".".join(str(loc) for loc in error["loc"])
                error_messages.append(f"{field}: {error['msg']}")
            return f"申請者情報が不正です: {', '.join(error_messages)}"
        
        # エージェントインスタンスを作成（session_managerが会話履歴を管理）
        agent = _get_travel_agent(session_id=state.session_id)
        
        # invocation_stateを渡してエージェント実行
        invocation_state = {
            "applicant_name": state.applicant_name,
            "application_date": state.application_date
        }
        
        response = agent(query, invocation_state=invocation_state)
        
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
    
    注意: session_managerがエージェントインスタンスと会話履歴を管理するため、
    このリセット関数は互換性のために残していますが、実際には何も行いません。
    リセットが必要な場合は、reception_agentで新しいsession_idを生成してください。
    """
    pass

