"""経費精算申請エージェント"""
from datetime import datetime, timedelta
from strands import Agent, tool, ToolContext
from strands import ModelRetryStrategy
from strands.agent.conversation_manager import SlidingWindowConversationManager
from strands_tools import image_reader
from tools.excel_generator import receipt_excel_generator
from session.session_manager import SessionManagerFactory
from handlers.human_approval_hook import HumanApprovalHook
from handlers.loop_control_hook import LoopControlHook


def _get_receipt_expense_system_prompt() -> str:
    """現在日付を含むシステムプロンプトを動的に生成"""
    today = datetime.now()
    three_months_ago = today - timedelta(days=90)
    
    return f"""あなたは経費精算申請エージェントです。

## 現在の日付情報
- 今日の日付: {today.strftime('%Y年%m月%d日')} ({today.strftime('%Y-%m-%d')})
- 3ヶ月前の日付: {three_months_ago.strftime('%Y年%m月%d日')} ({three_months_ago.strftime('%Y-%m-%d')})
- 申請可能な最古の日付: {three_months_ago.strftime('%Y-%m-%d')}
- **重要**: 領収書の日付が {three_months_ago.strftime('%Y-%m-%d')} ～{today.strftime('%Y-%m-%d')}の範囲であれば、過去3ヶ月以内として申請可能です

## 役割

1. **領収書画像の処理**
   - image_readerツールで画像から情報を抽出（店舗名、金額、日付、品目）

2. **経費区分の判断**
   - 品目を分析して適切な経費区分を判断：
     * 事務用品費: 書籍、文房具、オフィス用品など
     * 宿泊費: ホテル、宿泊施設など
     * 資格精算費: 資格試験、受験料、認定費用など
     * その他経費: 上記以外

3. **Excel申請書の生成**
   - receipt_excel_generatorツールで申請書を生成
   - 申請者名は自動的に取得されます（引数として渡す必要はありません）
   - 金額が30,000円を超える場合はエラーを返す

## 経費申請ルール（必須チェック項目）

### 1. 日付チェック
- 領収書の日付が {three_months_ago.strftime('%Y-%m-%d')} より前（3ヶ月を超える）の場合：
  * まず、ユーザーに日付の確認と修正を提案してください
  * 修正されない場合は、業務上の正当な理由を確認してください
  * 正当な理由がない場合は申請を受け付けないでください
- 領収書の日付が {three_months_ago.strftime('%Y-%m-%d')} ～{today.strftime('%Y-%m-%d')}の範囲である場合：
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

## 処理フロー
1. ユーザーから領収書画像のパスを収集
2. image_readerツールで画像から情報を抽出
3. 抽出した情報をユーザーに確認
4. **経費申請ルールに基づいてチェック**：
   - 日付が{three_months_ago.strftime('%Y-%m-%d')} ～{today.strftime('%Y-%m-%d')}の範囲か確認
   - 5,000円超の場合は上長承認を確認
   - 業務目的を確認
5. 必要に応じて修正を受け付ける
6. **重要**: すべての情報が揃い、ルールチェックが完了したら、**ユーザーに最終確認を求めずに**直接receipt_excel_generatorツールを実行してください
   - システムが自動的に承認プロセスを実行します
   - 修正が必要な場合は、システムから指示があります

## 重要な注意事項
- 領収書画像のパスは必ず確認してください
- 抽出した情報は必ずユーザーに確認してください
- 金額が30,000円を超える場合はエラーを通知してください
- **重要**: すべての情報が揃い、ルールチェックが完了したら、**ユーザーに「よろしいですか？」などの最終確認を求めずに**、直接receipt_excel_generatorツールを実行してください
- システムが自動的に承認プロセスを実行します
- 修正が必要な場合は、システムから指示があります
- 申請書の生成が完了したら、ファイルパスを明示してください
- receipt_excel_generatorツールを呼び出す際、applicant_nameパラメータは不要です（自動取得されます）
- ツールの実行結果に「キャンセルしました」というメッセージが含まれている場合は、ユーザーの指示に従ってください
 
常に丁寧で分かりやすい日本語で対話してください。
"""

# グローバル変数
receipt_expense_agent_instance = None
_session_manager = None

def _get_receipt_expense_agent(session_id: str = None) -> Agent:
    """
    経費精算申請エージェントのインスタンスを取得（シングルトンパターン）
    
    Args:
        session_id: セッションID（省略時はセッション管理なし）
    
    Returns:
        Agent: 経費精算申請エージェントのインスタンス
    """
    global receipt_expense_agent_instance, _session_manager
    
    if receipt_expense_agent_instance is None:
        # セッションマネージャーの作成（session_idが指定されている場合）
        if session_id:
            _session_manager = SessionManagerFactory.create_session_manager(session_id)
        
        # Human-in-the-Loop承認フックの作成
        approval_hook = HumanApprovalHook()
        
        # ループ制御フックの作成
        loop_control_hook = LoopControlHook(
            max_iterations=10,  # 専門エージェントは特定タスクに集中するため標準的な回数
            agent_name="経費精算申請エージェント"
        )
        
        # エージェントの初期化
        receipt_expense_agent_instance = Agent(
            model="jp.anthropic.claude-sonnet-4-5-20250929-v1:0",
            system_prompt=_get_receipt_expense_system_prompt(),
            tools=[
                image_reader,
                receipt_excel_generator
            ],
            conversation_manager=SlidingWindowConversationManager(
                window_size=15,  # 専門エージェントは特定タスクに集中するため小さめ
                should_truncate_results=True,
                per_turn=False
            ),
            agent_id="receipt_expense_agent",
            name="経費精算申請エージェント",
            description="領収書画像から情報を抽出し、Excel形式の経費精算申請書を自動生成します",
            callback_handler=None,  # ストリーミング出力を無効化
            retry_strategy=ModelRetryStrategy(
                max_attempts=6,
                initial_delay=4,
                max_delay=240
            ),
            session_manager=_session_manager,  # セッションマネージャーを設定
            hooks=[approval_hook, loop_control_hook]  # Human-in-the-Loop承認フックとループ制御フックを追加
        )
    
    return receipt_expense_agent_instance

#Agent as Tools
@tool(context=True)
def receipt_expense_agent(query: str, tool_context: ToolContext) -> str:
    """
    経費精算申請ツール
    
    領収書画像から情報を抽出し、Excel形式の経費精算申請書を自動生成します。
    会話履歴を保持するため、複数回の呼び出しで段階的に情報を収集できます。
    
    Args:
        query: ユーザーからの入力や質問
    
    Returns:
        str: エージェントからの応答
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.info("[receipt_expense_agent] ツールが呼び出されました")

    try:
        # invocation_stateからsession_idを取得
        session_id = None
        if tool_context and tool_context.invocation_state:
            session_id = tool_context.invocation_state.get("session_id")
        
        # エージェントインスタンスを取得（初回は初期化、2回目以降は既存インスタンスを使用）
        agent = _get_receipt_expense_agent(session_id=session_id)
        
        # invocation_stateから申請者名と申請日を取得
        applicant_name = None
        application_date = None
        if tool_context and tool_context.invocation_state:
            applicant_name = tool_context.invocation_state.get("applicant_name")
            application_date = tool_context.invocation_state.get("application_date")
        
        # エージェント実行（invocation_stateを渡す）
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
            return (
                "申し訳ございません。処理が複雑すぎて完了できませんでした。\n\n"
                "以下のいずれかをお試しください：\n"
                "1. 領収書を1枚ずつ申請してください\n"
                "2. より具体的な情報を提供してください\n"
                "3. 不要な情報を削除してください\n\n"
                "受付窓口に戻りますので、もう一度シンプルな内容でお試しください。"
            )
        else:
            return f"エラーが発生しました。受付窓口に戻ります。"
    
    except Exception as e:
        logger.error(f"[receipt_expense_agent] エラーが発生しました: {e}")
        return f"エラーが発生しました。受付窓口に戻ります。"


def reset_receipt_expense_agent():
    """
    経費精算申請エージェントの状態をリセット
    
    新しい申請を開始する際に呼び出すことで、会話履歴をクリアする。
    """
    global receipt_expense_agent_instance, _session_manager
    receipt_expense_agent_instance = None
    _session_manager = None

