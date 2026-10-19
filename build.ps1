$ErrorActionPreference = "Stop"

# Do not let unrelated image/PDF runtimes on PATH contribute Windows API-set
# stub DLLs to the PyInstaller bundle. Windows supplies these APIs itself.
$env:PATH = (($env:PATH -split ";") | Where-Object {
    $_ -notmatch "(?i)\\\.cache\\codex-runtimes\\.*\\dependencies\\native\\" -and
    $_ -notmatch "(?i)\\Program Files\\Eclipse Adoptium\\.*\\bin\\?$" -and
    $_ -notmatch "(?i)\\jdk-[^\\]*\\bin\\?$"
}) -join ";"

$pyinstaller = Get-Command pyinstaller -ErrorAction Stop
& $pyinstaller.Source --clean --noconfirm --onedir --windowed `
    --uac-admin `
    --name "KimoPCManager" `
    --icon "assets/icon.ico" `
    --add-data "locales;locales" `
    --add-data "assets;assets" `
    --distpath "dist\KimoPCManager-Verified" `
    --workpath "build\KimoPCManager-Verified" `
    main.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

# Leave one canonical distributable bundle. Remove only generated legacy builds
# after the new executable exists and has completed successfully.
$canonicalExe = Join-Path "dist\KimoPCManager-Verified\KimoPCManager" "KimoPCManager.exe"
if (-not (Test-Path $canonicalExe)) {
    throw "Build completed without the expected executable: $canonicalExe"
}
$projectPath = (Get-Location).Path
foreach ($legacy in @("dist\KimoPCManager", "dist\KimoPCManager-Current", "dist\KimoPCManager-Updated", "dist\KimoPCManager.previous", "build\KimoPCManager-Updated", "build\KimoPCManager")) {
    if (-not (Test-Path $legacy)) { continue }
    $legacyPath = (Resolve-Path $legacy).Path
    if (-not $legacyPath.StartsWith($projectPath, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to remove a path outside the project folder: $legacyPath"
    }
    try {
        Remove-Item -LiteralPath $legacyPath -Recurse -Force -ErrorAction Stop
    } catch {
        Write-Warning "Could not remove stale package '$legacyPath' because Windows still has a file open: $($_.Exception.Message)"
    }
}
exit 0
