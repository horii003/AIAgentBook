"""申請受付窓口エージェント
社内には「経費精算申請」「出張申請」「交通費精算申請」「稟議申請」など、様々な申請があります。
どういう場合にどこにどのような申請を出せばよいか分かりにくい課題があります。 

社員が「出張したい」「備品を購入したい」などの申請内容を入力すると、
申請受付窓口エージェントとしてユーザーからの申請内容を受け付け、適切な専門エージェントに振り分けます。

社員が申請ルールや申請方法が分からない方でも正しく申請できることを目的とします。
"""

import uuid
from datetime import datetime
from strands import Agent
from strands import ModelRetryStrategy
from strands.agent.conversation_manager import SlidingWindowConversationManager
from agents.travel_agent import travel_agent
from agents.receipt_expense_agent import receipt_expense_agent
from session.session_manager import SessionManagerFactory
from handlers.loop_control_hook import LoopControlHook
from prompt.prompt_reception import RECEPTION_SYSTEM_PROMPT
from config.model_config import ModelConfig

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
        
        # セッションIDをUUID + タイムスタンプで生成
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]  # UUIDの最初の8文字を使用
        self._session_id = f"{timestamp}_{unique_id}"
        
        # セッションマネージャーの作成
        self._session_manager = SessionManagerFactory.create_session_manager(self._session_id)
        
        # ループ制御フックの作成
        loop_control_hook = LoopControlHook(
            max_iterations=5,  # オーケストレーターは専門エージェントとのやり取りがあるため多めに設定
            agent_name="申請受付窓口エージェント"
        )
        
        # エージェントの初期化（セッションマネージャー付き）
        self.agent = Agent(
            model=ModelConfig.get_model(),
            system_prompt=RECEPTION_SYSTEM_PROMPT, #別モジュールから取得
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
            session_manager=self._session_manager,  # セッションマネージャーを設定
            hooks=[loop_control_hook]  # ループ制御フックを追加
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
                # invocation_stateとして申請者名、申請日、セッションIDを渡す
                response = self.agent(
                    user_input, 
                    invocation_state={
                        "applicant_name": self._applicant_name,
                        "application_date": datetime.now().strftime("%Y-%m-%d"),
                        "session_id": self._session_id
                    }
                )
                print(f"\nエージェント: {response}")
                
            except KeyboardInterrupt:
                print("\n\nエージェント: 処理を中断しました。")
                break
            except RuntimeError as e:
                # ループ制限エラーの処理
                if "エージェントループの制限" in str(e):
                    # ユーザーには分かりやすいメッセージ
                    print("\n" + "="*60)
                    print("【処理が複雑すぎます】")
                    print("="*60)
                    print("\n申し訳ございません。処理が複雑すぎて完了できませんでした。")
                    print("\n以下のいずれかをお試しください：")
                    print("1. タスクをより小さな単位に分割してください")
                    print("   例：複数の申請を一度に行う場合は、1つずつ申請してください")
                    print("2. より具体的な指示を提供してください")
                    print("   例：「交通費を申請したい」→「1月10日の東京から大阪への新幹線代を申請したい」")
                    print("3. 不要な情報を削除してください")
                    print("   例：申請に関係のない質問や情報は別途お尋ねください")
                    print("\n" + "="*60)
                    print("もう一度、シンプルな内容でお試しください。")
                    print("="*60 + "\n")
                else:
                    print(f"\nエラーが発生しました。もう一度お試しください。\n")
            except Exception as e:
                print(f"\nエラーが発生しました。もう一度お試しください。\n")
