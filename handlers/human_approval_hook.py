"""
Human-in-the-Loop承認フック

excel_generatorツールの実行前に人間の承認を求め、
修正要望があれば修正を実行するフック。
"""

from typing import Any
from strands.hooks import HookProvider, HookRegistry, BeforeToolCallEvent
import logging

logger = logging.getLogger(__name__)


class HumanApprovalHook(HookProvider):
    """
    excel_generatorツール実行前に人間の承認を求めるフック
    
    このフックは以下の機能を提供します：
    1. excel_generatorツール実行前に承認を求める
    2. 承認された場合はツールを実行
    3. 修正要望がある場合はツール実行をキャンセルし、修正を促す
    4. 拒否された場合はツール実行をキャンセル
    """
    
    def __init__(self, approval_callback=None):
        """
        初期化
        
        Args:
            approval_callback: 承認を求めるコールバック関数
                               引数: tool_name (str), tool_params (dict)
                               戻り値: tuple (approved: bool, feedback: str)
                               - approved: True=承認, False=拒否または修正要望
                               - feedback: 修正要望の内容（承認時は空文字列）
        """
        self.approval_callback = approval_callback or self._default_approval_callback
    
    def register_hooks(self, registry: HookRegistry, **kwargs: Any) -> None:
        """フックの登録"""
        registry.add_callback(BeforeToolCallEvent, self.request_approval)
    
    def request_approval(self, event: BeforeToolCallEvent) -> None:
        """
        ツール実行前に承認を求める
        
        Args:
            event: BeforeToolCallEvent
        """
        tool_name = event.tool_use["name"]
        
        # excel_generatorツールのみを対象とする
        if not (tool_name == "receipt_excel_generator" or tool_name == "travel_excel_generator"):
            return
        
        tool_params = event.tool_use.get("input", {})
        
        logger.info(f"ツール実行前の承認を求めています: {tool_name}")
        logger.info(f"パラメータ: {tool_params}")
        
        # 承認コールバックを呼び出し
        approved, feedback = self.approval_callback(tool_name, tool_params)
        
        if approved:
            logger.info(f"ツール実行が承認されました: {tool_name}")
            # 承認された場合は何もしない（ツールが実行される）
            return
        else:
            # 拒否または修正要望の場合はツール実行をキャンセル
            if feedback:
                logger.info(f"修正要望またはキャンセル: {feedback}")
                # キャンセルの場合は特別なメッセージ
                if feedback.upper() == "CANCEL":
                    cancel_message = (
                        "ユーザーが申請をキャンセルしました。\n\n"
                        "承知いたしました。申請をキャンセルいたしました。\n"
                        "他に申請したい内容があればお申し付けください。\n"
                        "なければ、これで受付を終了いたします。"
                    )
                else:
                    # 通常の修正要望
                    cancel_message = (
                        f"ユーザーから修正要望がありました: {feedback}\n\n"
                        f"修正内容を反映して、もう一度申請内容を確認してください。"
                    )
            else:
                # feedbackが空の場合もキャンセルとして扱う（後方互換性）
                logger.info(f"ツール実行がキャンセルされました: {tool_name}")
                cancel_message = (
                    "ユーザーが申請をキャンセルしました。\n\n"
                    "承知いたしました。申請をキャンセルいたしました。\n"
                    "他に申請したい内容があればお申し付けください。\n"
                    "なければ、これで受付を終了いたします。"
                )
            
            event.cancel_tool = cancel_message
    
    def _default_approval_callback(self, tool_name: str, tool_params: dict) -> tuple:
        """
        デフォルトの承認コールバック（コンソール入力）
        
        Args:
            tool_name: ツール名
            tool_params: ツールパラメータ
        
        Returns:
            tuple: (approved: bool, feedback: str)
        """
        print("\n" + "="*60)
        print("【最終確認】申請書を生成します")
        print("="*60)
        
        # パラメータを見やすく表示
        if tool_name == "receipt_excel_generator":
            print(f"店舗名: {tool_params.get('store_name', 'N/A')}")
            print(f"金額: ¥{tool_params.get('amount', 0):,.0f}")
            print(f"日付: {tool_params.get('date', 'N/A')}")
            print(f"品目: {', '.join(tool_params.get('items', []))}")
            print(f"経費区分: {tool_params.get('expense_category', 'N/A')}")
        elif tool_name == "travel_excel_generator":
            routes = tool_params.get('routes', [])
            print(f"経路数: {len(routes)}件")
            total_cost = sum(route.get('cost', 0) for route in routes)
            print(f"合計金額: ¥{total_cost:,.0f}")
            print("\n経路詳細:")
            for i, route in enumerate(routes, 1):
                print(f"  {i}. {route.get('date', 'N/A')}: "
                      f"{route.get('departure', 'N/A')} → {route.get('destination', 'N/A')} "
                      f"({route.get('transport_type', 'N/A')}) ¥{route.get('cost', 0):,.0f}")
        
        print("-"*60)
        print("1. OK（申請書を生成）")
        print("2. 修正したい")
        print("3. キャンセル")
        
        while True:
            choice = input("\n選択 (1-3): ").strip()
            
            if choice == "1":
                print("\n✓ 申請書を生成します...\n")
                return True, ""
            elif choice == "2":
                feedback = input("\n修正内容を入力してください: ").strip()
                if feedback:
                    print(f"\n✓ 修正要望: {feedback}\n")
                    return False, feedback
                else:
                    print("修正内容を入力してください。")
            elif choice == "3":
                print("\n✗ キャンセルしました。\n")
                return False, "CANCEL"
            else:
                print("1、2、または3を入力してください。")
