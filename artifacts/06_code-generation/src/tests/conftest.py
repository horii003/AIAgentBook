"""テスト共通フィクスチャ定義"""
import json
import os
import pytest
import openpyxl


@pytest.fixture
def tmp_data_dir(tmp_path, monkeypatch):
    """テスト用一時データディレクトリ（train_fares.json・fixed_fares.json）"""
    import tools.transport_tools as tt
    train_data = [
        {"departure": "東京", "destination": "大阪", "fare": 13240.0},
        {"departure": "大阪", "destination": "東京", "fare": 13240.0},
    ]
    fixed_data = {"バス": 500.0, "タクシー": 1000.0, "飛行機": 20000.0}
    train_file = tmp_path / "train_fares.json"
    fixed_file = tmp_path / "fixed_fares.json"
    train_file.write_text(json.dumps(train_data), encoding="utf-8")
    fixed_file.write_text(json.dumps(fixed_data), encoding="utf-8")
    monkeypatch.setattr(tt, "_TRAIN_FARES_PATH", str(train_file))
    monkeypatch.setattr(tt, "_FIXED_FARES_PATH", str(fixed_file))
    monkeypatch.setattr(tt, "_train_fares_loaded", False)
    monkeypatch.setattr(tt, "_fixed_fares_loaded", False)
    return tmp_path


@pytest.fixture
def tmp_template_dir(tmp_path, monkeypatch):
    """テスト用一時テンプレートディレクトリ"""
    import tools.output_generator as og
    wb = openpyxl.Workbook()
    transport_path = str(tmp_path / "transport_template.xlsx")
    expense_path = str(tmp_path / "expense_template.xlsx")
    wb.save(transport_path)
    wb.save(expense_path)
    monkeypatch.setattr(og, "_TRANSPORT_TEMPLATE_PATH", transport_path)
    monkeypatch.setattr(og, "_EXPENSE_TEMPLATE_PATH", expense_path)
    monkeypatch.setattr(og, "_OUTPUT_DIR", str(tmp_path / "output"))
    return tmp_path


@pytest.fixture
def sample_transport_items():
    """テスト用移動明細リスト"""
    return [
        {
            "travel_date": "2026-05-10",
            "departure": "東京",
            "destination": "大阪",
            "transport_type": "電車",
            "fare": 13240.0,
            "purpose": "出張",
        }
    ]


@pytest.fixture
def sample_expense_items():
    """テスト用経費明細リスト"""
    return [
        {
            "purchase_date": "2026-05-10",
            "item_name": "ノート",
            "amount": 500.0,
            "expense_category": "事務用品費",
            "purpose": "業務用",
        }
    ]
