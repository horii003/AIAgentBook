# ============================================================
# AIAgentBook ダウンロード資材 zip 作成スクリプト
#
# 仕様:
#   - AIAgentBook 配下を zip 圧縮する
#   - zip ファイル名は「AiAgentBook.zip」
#   - 解凍すると AIAgentBook フォルダ配下の .kiro フォルダなどが
#     トップフォルダなしで直接配置される状態になる
#   - zip 対象外:
#       - フォルダ「ダウンロード資材」「.venv」「.git」
#       - AIAgentBook フォルダ直下のファイルのうち、requirements.txt 以外のファイル
#   （上記除外フォルダ以外の直下サブフォルダはすべて含める）
#
# 本スクリプトは create_dl_material.bat から呼び出される想定。
# ============================================================

$ErrorActionPreference = 'Stop'

try {
    # --- パス定義 ---
    # このスクリプトは AIAgentBook\ダウンロード資材\ に配置される
    $scriptDir = $PSScriptRoot
    # AIAgentBook のルート（1つ上の階層）
    $srcRoot = (Resolve-Path (Join-Path $scriptDir '..')).Path

    $zipName = 'AiAgentBook.zip'
    $zipPath = Join-Path $scriptDir $zipName

    # ステージング用の一時ディレクトリ
    # 解凍時にトップフォルダを作らないため、中身をステージングルート直下に配置する
    $stageDir = Join-Path $env:TEMP ("dl_material_stage_" + [System.Guid]::NewGuid().ToString('N'))
    $stageTop = $stageDir

    Write-Host "[情報] ソースルート : $srcRoot"
    Write-Host "[情報] 出力zip      : $zipPath"
    Write-Host "[情報] ステージング : $stageDir"
    Write-Host ""

    # --- 既存zipの削除 ---
    if (Test-Path -LiteralPath $zipPath) {
        Write-Host "[情報] 既存のzipファイルを削除します。"
        Remove-Item -LiteralPath $zipPath -Force
    }

    # --- ステージングディレクトリ作成 ---
    if (Test-Path -LiteralPath $stageDir) {
        Remove-Item -LiteralPath $stageDir -Recurse -Force
    }
    New-Item -ItemType Directory -Path $stageDir -Force | Out-Null

    # --- 対象のコピー ---
    # 修正版仕様:
    #   - 直下のサブフォルダは除外対象を除きすべて含める（中身ごと）
    #   - 直下のファイルは requirements.txt のみ含める（他の直下ファイルは除外）
    #   - 除外フォルダ: 「ダウンロード資材」「.venv」「.git」
    $excludeDirs = @('ダウンロード資材', '.venv', '.git')
    $keepFile    = 'requirements.txt'

    # 直下のサブフォルダをコピー（除外フォルダを除く）
    # -Force を付与して隠し属性フォルダ（.git 等）も列挙対象にし、除外判定を確実にする
    Get-ChildItem -LiteralPath $srcRoot -Directory -Force | Where-Object {
        $excludeDirs -notcontains $_.Name
    } | ForEach-Object {
        Write-Host "[情報] フォルダをコピー: $($_.Name)"
        Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $stageTop $_.Name) -Recurse -Force
    }

    # 直下のファイルは requirements.txt のみコピー
    $reqSrc = Join-Path $srcRoot $keepFile
    if (-not (Test-Path -LiteralPath $reqSrc)) {
        throw "$keepFile が見つかりません: $reqSrc"
    }
    Copy-Item -LiteralPath $reqSrc -Destination (Join-Path $stageTop $keepFile) -Force
    Write-Host "[情報] $keepFile をコピーしました。"

    # --- zip 圧縮 ---
    # 解凍するとトップフォルダなしで中身（.kiro 等）が直接展開されるよう、
    # ステージングルート直下の各項目を圧縮対象にする。
    Write-Host "[情報] zip を作成します..."
    $itemsToZip = Get-ChildItem -LiteralPath $stageDir -Force | Select-Object -ExpandProperty FullName
    Compress-Archive -Path $itemsToZip -DestinationPath $zipPath -Force

    Write-Host ""
    Write-Host "[完了] zip を作成しました: $zipPath"

    # --- 後片付け ---
    Remove-Item -LiteralPath $stageDir -Recurse -Force
    exit 0
}
catch {
    Write-Host ""
    Write-Host "[エラー] $($_.Exception.Message)"
    Write-Host "[中断] 処理を中断しました。"
    if ($stageDir -and (Test-Path -LiteralPath $stageDir)) {
        Remove-Item -LiteralPath $stageDir -Recurse -Force
    }
    exit 1
}
