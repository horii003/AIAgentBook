"""ReceiptExpenseInputモデルのバリデーションテスト"""
import pytest
from pydantic import ValidationError
from models.data_models import ReceiptExpenseInput


class TestReceiptExpenseInputValidation:
    """ReceiptExpenseInputモデルのバリデーションテスト"""
    
    def test_valid_receipt_expense_input(self):
        """正常な入力データの検証"""
        receipt = ReceiptExpenseInput(
            store_name="コンビニA",
            amount=1500.0,
            date="2025-01-15",
            items=["ボールペン", "ノート"],
            expense_category="事務用品費"
        )
        assert receipt.store_name == "コンビニA"
        assert receipt.amount == 1500.0
        assert receipt.date == "2025-01-15"
        assert receipt.items == ["ボールペン", "ノート"]
        assert receipt.expense_category == "事務用品費"
        print("✅ 正常な入力データは問題なく作成できる")
    
    def test_empty_store_name(self):
        """空の店舗名の検証"""
        with pytest.raises(ValidationError) as exc_info:
            ReceiptExpenseInput(
                store_name="",  # 空文字列は許可されない
                amount=1500.0,
                date="2025-01-15",
                items=["ボールペン"],
                expense_category="事務用品費"
            )
        
        error = exc_info.value.errors()[0]
        assert "store_name" in str(error["loc"])
        print(f"✅ 空の店舗名を検出: {error['msg']}")
    
    def test_zero_amount(self):
        """金額が0の検証"""
        with pytest.raises(ValidationError) as exc_info:
            ReceiptExpenseInput(
                store_name="コンビニA",
                amount=0.0,  # 0は許可されない（gt=0）
                date="2025-01-15",
                items=["ボールペン"],
                expense_category="事務用品費"
            )
        
        error = exc_info.value.errors()[0]
        assert "amount" in str(error["loc"])
        print(f"✅ 金額0を検出: {error['msg']}")
    
    def test_negative_amount(self):
        """負の金額の検証"""
        with pytest.raises(ValidationError) as exc_info:
            ReceiptExpenseInput(
                store_name="コンビニA",
                amount=-1500.0,  # 負の金額は許可されない
                date="2025-01-15",
                items=["ボールペン"],
                expense_category="事務用品費"
            )
        
        error = exc_info.value.errors()[0]
        assert "amount" in str(error["loc"])
        print(f"✅ 負の金額を検出: {error['msg']}")
    
    def test_invalid_date_format(self):
        """無効な日付形式の検証"""
        with pytest.raises(ValidationError) as exc_info:
            ReceiptExpenseInput(
                store_name="コンビニA",
                amount=1500.0,
                date="2025/01/15",  # スラッシュ区切りは無効
                items=["ボールペン"],
                expense_category="事務用品費"
            )
        
        error = exc_info.value.errors()[0]
        assert "date" in str(error["loc"])
        assert "YYYY-MM-DD" in str(error["msg"])
        print(f"✅ 無効な日付形式を検出: {error['msg']}")
    
    def test_invalid_date_value(self):
        """無効な日付値の検証"""
        with pytest.raises(ValidationError) as exc_info:
            ReceiptExpenseInput(
                store_name="コンビニA",
                amount=1500.0,
                date="2025-13-45",  # 存在しない日付
                items=["ボールペン"],
                expense_category="事務用品費"
            )
        
        error = exc_info.value.errors()[0]
        assert "date" in str(error["loc"])
        print(f"✅ 無効な日付値を検出: {error['msg']}")
    
    def test_empty_items_list(self):
        """空の品目リストの検証"""
        with pytest.raises(ValidationError) as exc_info:
            ReceiptExpenseInput(
                store_name="コンビニA",
                amount=1500.0,
                date="2025-01-15",
                items=[],  # 空リストは許可されない（min_length=1）
                expense_category="事務用品費"
            )
        
        error = exc_info.value.errors()[0]
        assert "items" in str(error["loc"])
        print(f"✅ 空の品目リストを検出: {error['msg']}")
    
    def test_empty_expense_category(self):
        """空の経費区分の検証"""
        with pytest.raises(ValidationError) as exc_info:
            ReceiptExpenseInput(
                store_name="コンビニA",
                amount=1500.0,
                date="2025-01-15",
                items=["ボールペン"],
                expense_category=""  # 空文字列は許可されない
            )
        
        error = exc_info.value.errors()[0]
        assert "expense_category" in str(error["loc"])
        print(f"✅ 空の経費区分を検出: {error['msg']}")
    
    def test_missing_required_field(self):
        """必須フィールドの欠落検証"""
        with pytest.raises(ValidationError) as exc_info:
            ReceiptExpenseInput(
                store_name="コンビニA",
                amount=1500.0,
                date="2025-01-15",
                items=["ボールペン"]
                # expense_category が欠落
            )
        
        error = exc_info.value.errors()[0]
        assert "expense_category" in str(error["loc"])
        assert "missing" in error["type"] or "required" in error["type"]
        print(f"✅ 必須フィールドの欠落を検出: {error['msg']}")
    
    def test_multiple_items(self):
        """複数の品目の検証"""
        receipt = ReceiptExpenseInput(
            store_name="文房具店",
            amount=3500.0,
            date="2025-01-15",
            items=["ボールペン", "ノート", "クリアファイル", "付箋"],
            expense_category="事務用品費"
        )
        assert len(receipt.items) == 4
        assert "ボールペン" in receipt.items
        assert "付箋" in receipt.items
        print("✅ 複数の品目を正常に処理")
    
    def test_string_to_float_coercion(self):
        """文字列から数値への自動変換"""
        receipt = ReceiptExpenseInput(
            store_name="コンビニA",
            amount="1500",  # 文字列で渡しても自動的にfloatに変換される
            date="2025-01-15",
            items=["ボールペン"],
            expense_category="事務用品費"
        )
        
        assert isinstance(receipt.amount, float)
        assert receipt.amount == 1500.0
        print("✅ 文字列から数値への自動変換が機能")
    
    def test_invalid_type_coercion(self):
        """変換できない型の検証"""
        with pytest.raises(ValidationError) as exc_info:
            ReceiptExpenseInput(
                store_name="コンビニA",
                amount="千五百円",  # 数値に変換できない文字列
                date="2025-01-15",
                items=["ボールペン"],
                expense_category="事務用品費"
            )
        
        error = exc_info.value.errors()[0]
        assert "amount" in str(error["loc"])
        print(f"✅ 変換できない型を検出: {error['msg']}")
    
    def test_multiple_validation_errors(self):
        """複数のバリデーションエラーを同時に検出"""
        with pytest.raises(ValidationError) as exc_info:
            ReceiptExpenseInput(
                store_name="",  # エラー1: 空の店舗名
                amount=-1500.0,  # エラー2: 負の金額
                date="2025/01/15",  # エラー3: 無効な日付形式
                items=[],  # エラー4: 空の品目リスト
                expense_category=""  # エラー5: 空の経費区分
            )
        
        errors = exc_info.value.errors()
        assert len(errors) >= 3  # 複数のエラーが検出される
        
        print(f"✅ 複数のエラーを同時に検出: {len(errors)}個")
        for error in errors:
            print(f"   - {error['loc']}: {error['msg']}")
    
    def test_dict_to_receipt_expense_input(self):
        """辞書からReceiptExpenseInputへの変換テスト"""
        data = {
            "store_name": "コンビニA",
            "amount": 1500.0,
            "date": "2025-01-15",
            "items": ["ボールペン", "ノート"],
            "expense_category": "事務用品費"
        }
        
        receipt = ReceiptExpenseInput(**data)
        assert receipt.store_name == "コンビニA"
        assert receipt.amount == 1500.0
        assert receipt.date == "2025-01-15"
        assert receipt.items == ["ボールペン", "ノート"]
        assert receipt.expense_category == "事務用品費"
        print("✅ 辞書からの変換が正常に機能")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
