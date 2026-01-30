"""申請受付窓口エージェント
社内には「経費精算申請」「出張申請」「交通費精算申請」「稟議申請」など、様々な申請があります。
どういう場合にどこにどのような申請を出せばよいか分かりにくい課題があります。 

社員が「出張したい」「備品を購入したい」などの申請内容を入力すると、
申請受付窓口エージェントとしてユーザーからの申請内容を受け付け、適切な専門エージェントに振り分けます。

社員が申請ルールや申請方法が分からない方でも正しく申請できることを目的とします。
"""

from strands import Agent
from strands import ModelRetryStrategy
from strands.agent.conversation_manager import SlidingWindowConversationManager
from agents.travel_agent import travel_agent, reset_travel_agent
from agents.receipt_expense_agent import receipt_expense_agent, reset_receipt_expense_agent
from session.session_manager import SessionManagerFactory

# システムプロンプト
RECEPTION_SYSTEM_PROMPT = """あなたは申請受付窓口エージェントです。
ユーザーからの申請依頼内容に応じて、
専門エージェントである「交通費精算申請エージェント(travel_agent)」と
「経費精算申請エージェント(receipt_expense_agent)」のどちらか適切なエージェントに
業務を引き継いでください。

処理の流れは以下を参照してください。
1. ユーザーから申請内容を収集してください。
2. 申請内容を分析して、処理をするのに最も適切な専門エージェントを特定します
   -「交通費精算申請エージェント(travel_agent)」：顧客訪問や出張などに発生した交通費だけの精算に関するもの
   - 「経費精算申請エージェント(receipt_expense_agent)」:領収書画像を使った経費精算に関するもの
3. 各専門エージェントの処理結果を確認：
   - 申請書が正常に生成された場合：「処理が完了しました」と伝える
   - 申請がキャンセルされた場合：専門エージェントからのメッセージをそのまま伝える（「完了」とは言わない）
4. 再度ユーザーに他に申請したい内容はあるか確認する
5. すべての申請受付を終えたら、処理を終了してください。


主な責任
 - 申請したい内容を正確に分類すること
 - 適切な専門エージェントにリクエストを振り分けること
 - 複数のエージェントが関与する場合に一貫した回答を確保すること
 - 専門エージェントからの応答を正確にユーザーに伝えること

判断プロトコル
 - 顧客訪問や会議、出張などの移動で発生した交通費用の申請 → 「交通費精算申請エージェント(travel_agent)」
 - 領収書画像を使った経費の申請、物品の購入費用、資格や研修費用、接待などの経費精算 → 「経費精算申請エージェント(receipt_expense_agent)」


常に丁寧で分かりやすい日本語で対話してください。
"""

class ReceptionAgent:
    # 初期化
    def __init__(self):
        self._applicant_initialized = False
        self._applicant_name = None  # 申請者名を保持
        self._session_id = None  # セッションIDを保持
        self._session_manager = None  # セッションマネージャーを保持
        self.agent = None  # エージェントは後で初期化


    def _initialize_applicant_info(self):
        """申請者情報を初期化"""
        if self._applicant_initialized:
            return
        
        print("\n" + "=" * 60)
        print("初期設定")
        print("=" * 60)
        
        # 申請者名の入力
        while True:
            applicant_name = input("申請者名を入力してください: ").strip()
            if applicant_name:
                break
            print("申請者名は必須です。もう一度入力してください。")
        
        # インスタンス変数に保存
        self._applicant_name = applicant_name
        
        # セッションIDを申請者名から生成（実際の運用では、より適切なID生成方法を使用）
        self._session_id = f"user_{applicant_name.replace(' ', '_')}"
        
        # セッションマネージャーの作成
        self._session_manager = SessionManagerFactory.create_session_manager(self._session_id)
        
        # エージェントの初期化（セッションマネージャー付き）
        self.agent = Agent(
            model="jp.anthropic.claude-sonnet-4-5-20250929-v1:0",
            system_prompt=RECEPTION_SYSTEM_PROMPT,
            tools=[travel_agent, receipt_expense_agent],
            conversation_manager=SlidingWindowConversationManager(
                window_size=30,  # オーケストレーターは複数エージェントとのやり取りを保持するため大きめ
                should_truncate_results=True,
                per_turn=False
            ),
            agent_id="reception_agent",
            name="申請受付窓口エージェント",
            description="ユーザーからの申請内容を受け付け、適切な専門エージェントに振り分けます",
            callback_handler=None,  # ストリーミング出力を無効化
            retry_strategy=ModelRetryStrategy(
                max_attempts=6,
                initial_delay=4,
                max_delay=240
            ),
            session_manager=self._session_manager  # セッションマネージャーを設定
        )
        
        self._applicant_initialized = True
        
        print(f"\n申請者情報を登録しました: {applicant_name}")
        print(f"セッションID: {self._session_id}")
        print("=" * 60)

    # 実行
    def run(self):
        """エージェントを実行"""
        print("=" * 60)
        print("こちらは申請受付窓口エージェントです")
        print("社内の様々な申請作業をサポートします")
        print("申請したい内容を教えてください。キーワードでも構いません")
        print("※終了するには 'exit' または 'quit' と入力ください")
        print("※最初からやり直すには 'reset' と入力ください")
        print("=" * 60)
        
        # 申請者情報の初期化
        self._initialize_applicant_info()

        # 対話ループ
        while True:
            try:  
                # ユーザー入力の受付
                user_input = input("\n\n入力内容(終了時は'quit'):").strip()
                
                # 終了時の処理
                if user_input.lower() in ["exit", "quit", "終了"]:
                    print("\nエージェント: ご利用ありがとうございました。")
                    break
                
                # リセット処理
                if user_input.lower() in ["reset", "リセット", "最初から"]:
                    reset_travel_agent()
                    reset_receipt_expense_agent()
                    self._applicant_name = None
                    self._applicant_initialized = False
                    self._session_id = None
                    self._session_manager = None
                    self.agent = None
                    print("\nエージェント: 会話履歴と申請者情報をリセットしました。")
                    self._initialize_applicant_info()
                    print("新しい申請を開始できます。")
                    continue
                
                # 空入力のスキップ
                if not user_input:
                    continue
                
                # エージェントの実行（専門エージェントツールが自動的に呼び出される）
                # invocation_stateとして申請者名とセッションIDを渡す
                response = self.agent(
                    user_input, 
                    invocation_state={
                        "applicant_name": self._applicant_name,
                        "session_id": self._session_id
                    }
                )
                print(f"\nエージェント: {response}")
                
            except KeyboardInterrupt:
                print("\n\nエージェント: 処理を中断しました。")
                break
            except Exception as e:
                print(f"\nエラーが発生しました: {e}")
                print("もう一度お試しください。\n")    


