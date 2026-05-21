"""E2Eテストスクリプト。

main.py を起動し、標準入力をパイプで渡して申請書生成までを自動確認する。
交通費申請と経費申請の両方をテストする。
"""
import glob
import os
import subprocess
import sys
import time


def run_e2e(label: str, inputs: list[str], timeout: int = 180) -> dict:
    """E2Eテストを実行する。

    Args:
        label: テストラベル
        inputs: 標準入力として渡す文字列リスト（改行区切りで結合）
        timeout: タイムアウト秒数

    Returns:
        dict: {"success": bool, "stdout": str, "stderr": str, "output_files": list}
    """
    stdin_text = "\n".join(inputs) + "\n"
    print(f"\n{'='*60}")
    print(f"[E2E] {label} 開始")
    print(f"{'='*60}")
    print(f"入力シナリオ:\n  " + "\n  ".join(inputs))
    print()

    # output ディレクトリの既存ファイルを記録
    before_files = set(glob.glob("output/*.xlsx"))

    result = subprocess.run(
        [sys.executable, "main.py"],
        input=stdin_text,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=timeout,
        cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    )

    # 新規生成ファイルを検出
    after_files = set(glob.glob("output/*.xlsx"))
    new_files = sorted(after_files - before_files)

    print("--- stdout ---")
    print(result.stdout[-3000:] if len(result.stdout) > 3000 else result.stdout)
    if result.stderr:
        print("--- stderr (末尾) ---")
        print(result.stderr[-1000:] if len(result.stderr) > 1000 else result.stderr)

    success = result.returncode == 0 and len(new_files) > 0
    print(f"\n[結果] returncode={result.returncode}, 新規ファイル={new_files}")
    print(f"[判定] {'✅ 成功' if success else '❌ 失敗'}")

    return {
        "success": success,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "output_files": new_files,
    }


def main():
    src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(src_dir)
    os.makedirs("output", exist_ok=True)

    results = []

    # ---- テスト1: 交通費申請 ----
    # 入力シナリオ: 申請者名 → 申請内容（1メッセージで全情報） → 以上です → OK → 承認[1] → quit
    r1 = run_e2e(
        label="交通費申請 E2Eテスト",
        inputs=[
            "テスト太郎",                          # 申請者名
            "2026-05-20に東京から新宿まで電車で移動しました。営業訪問のためです。交通費を申請したいです。",
            "以上です",                            # 追加区間なし
            "OK",                                  # ドラフト確認OK
            "1",                                   # HumanApprovalHook: 承認
            "quit",
        ],
    )
    results.append(("交通費申請", r1))

    time.sleep(2)

    # ---- テスト2: 経費申請 ----
    r2 = run_e2e(
        label="経費申請 E2Eテスト",
        inputs=[
            "テスト花子",                          # 申請者名
            "2026-05-20にAmazonでボールペンを500円で購入しました。事務用品費です。業務用です。経費精算を申請したいです。",
            "以上です",                            # 追加経費なし
            "OK",                                  # ドラフト確認OK
            "1",                                   # HumanApprovalHook: 承認
            "quit",
        ],
    )
    results.append(("経費申請", r2))

    # ---- 結果サマリー ----
    print(f"\n{'='*60}")
    print("E2Eテスト結果サマリー")
    print(f"{'='*60}")
    all_ok = True
    for label, r in results:
        status = "✅ 成功" if r["success"] else "❌ 失敗"
        files = r["output_files"]
        print(f"  {label}: {status}")
        for f in files:
            print(f"    → {f}")
        if not r["success"]:
            all_ok = False

    print(f"\n総合判定: {'✅ 全テスト成功' if all_ok else '❌ 一部失敗'}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
