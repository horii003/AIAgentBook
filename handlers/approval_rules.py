"""
申請ルールエンジンモジュール

経費精算申請の承認ルールを提供します。
経費区分の分類はLLMが直接判断するため、このモジュールでは金額チェックのみを提供します。
"""

from typing import Tuple


class ApprovalRuleEngine:
    """
    申請ルールエンジン
    
    経費精算申請の金額チェックを行うユーティリティクラス。
    経費区分の分類はLLMが直接判断するため、ここでは金額制限のみを扱います。
    """
    
    # 最大申請金額（円）
    MAX_AMOUNT = 30000
    
    # 経費区分のガイドライン（LLMがシステムプロンプトで参照）
    EXPENSE_CATEGORIES = {
        "事務用品費": "書籍、文房具、オフィス用品、ノート、ペンなど",
        "宿泊費": "ホテル、宿泊施設など",
        "資格精算費": "資格試験、受験料、認定費用など",
        "その他経費": "上記以外の経費"
    }
    
    @staticmethod
    def check_amount(amount: float) -> Tuple[bool, str]:
        """
        金額チェック（承認可否とメッセージを返却）
        
        申請金額が30,000円以下であれば承認、超過していれば拒否します。
        
        Args:
            amount: チェック対象の金額（円）
            
        Returns:
            Tuple[bool, str]: (承認可否, メッセージ)
                - 承認の場合: (True, "承認されました")
                - 拒否の場合: (False, "金額が制限を超えています。最大金額: 30,000円")
        
        Examples:
            >>> ApprovalRuleEngine.check_amount(25000)
            (True, "承認されました")
            
            >>> ApprovalRuleEngine.check_amount(35000)
            (False, "金額が制限を超えています。最大金額: 30,000円")
        """
        if amount <= ApprovalRuleEngine.MAX_AMOUNT:
            return (True, "承認されました")
        else:
            return (False, f"金額が制限を超えています。最大金額: {ApprovalRuleEngine.MAX_AMOUNT:,}円")
