# -*- coding: utf-8 -*-
"""エンドツーエンドテストスクリプト

main.pyを起動し、交通費精算申請書が生成されるまでの一連の流れを自動実行する。
stdin自動入力でインタラクティブなCLI操作をシミュレートする。
"""
import subprocess
import sys
import os
import glob
import time
from datetime import datetime

# Windows環境でのUnicode出力対応
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


def run_e2e_test():
    """E2Eテストを実行する"""
    src_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(src_dir, "output")

    # テスト前のoutputディレクトリのファイル一覧を記録
    os.makedirs(output_dir, exist_ok=True)
    before_files = set(glob.glob(os.path.join(output_dir, "*.xlsx")))
    print(f"テスト前のoutputファイル数: {len(before_files)}")

    # stdin自動入力シーケンス
    # フロー:
    #   1. 申請者名入力
    #   2. 交通費申請の依頼（移動情報を一度に提供）
    #   3. 追加区間なし（「以上です」）
    #   4. HumanApprovalHookの承認ダイアログ（"1" = OK）
    #   5. quit で終了
    stdin_inputs = [
        "テスト太郎",                          # 申請者名
        "交通費の申請をしたいです。2026-05-01に渋谷から新宿まで電車で移動しました。業務目的は顧客訪問です。",  # 申請内容＋移動情報
        "以上です",                            # 追加区間なし
        "1",                                   # HumanApprovalHookの承認（OK）
        "quit",                                # 終了
    ]

    # 入力を改行で結合
    stdin_text = "\n".join(stdin_inputs) + "\n"

    print("=" * 60)
    print("E2Eテスト開始")
    print(f"開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print("\n【自動入力シーケンス】")
    for i, inp in enumerate(stdin_inputs, 1):
        print(f"  {i}. {inp}")
    print()

    # main.pyをサブプロセスで起動
    start_time = time.time()
    try:
        result = subprocess.run(
            [sys.executable, "-X", "utf8", "main.py"],
            input=stdin_text,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=src_dir,
            timeout=300,  # 5分タイムアウト
            env={**os.environ, "PYTHONUTF8": "1"},
        )
    except subprocess.TimeoutExpired:
        print("TIMEOUT: 5分以内に処理が完了しませんでした")
        return False

    elapsed = time.time() - start_time

    # 出力表示
    print("【標準出力】")
    print(result.stdout)

    if result.stderr:
        print("【標準エラー出力（ERRORレベルのみ）】")
        error_lines = [
            line for line in result.stderr.splitlines()
            if "[ERROR]" in line or "Traceback" in line or "Error:" in line
        ]
        if error_lines:
            for line in error_lines[:20]:
                print(line)
        else:
            print("  （ERRORレベルのログなし）")

    print(f"\n実行時間: {elapsed:.1f}秒")
    print(f"終了コード: {result.returncode}")

    # テスト後のoutputディレクトリのファイル一覧を確認
    after_files = set(glob.glob(os.path.join(output_dir, "*.xlsx")))
    new_files = after_files - before_files

    print("\n" + "=" * 60)
    print("【テスト結果】")
    print("=" * 60)

    if new_files:
        print(f"[OK] 申請書ファイルが生成されました（{len(new_files)}件）")
        for f in sorted(new_files):
            size = os.path.getsize(f)
            print(f"   {os.path.basename(f)} ({size:,} bytes)")
        return True
    else:
        print("[FAIL] 申請書ファイルが生成されませんでした")
        print("\n【デバッグ情報】")
        print(f"outputディレクトリ: {output_dir}")
        print(f"テスト前ファイル数: {len(before_files)}")
        print(f"テスト後ファイル数: {len(after_files)}")
        return False


if __name__ == "__main__":
    success = run_e2e_test()
    sys.exit(0 if success else 1)
