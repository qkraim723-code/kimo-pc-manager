$currentDir = (Get-Location).Path
$wsh = New-Object -ComObject WScript.Shell
$shortcutPath = Join-Path $currentDir "Kimo PC Manager.lnk"
$targetExe = Join-Path $currentDir "dist\KimoPCManager-Verified\KimoPCManager\KimoPCManager.exe"
$workingDir = Join-Path $currentDir "dist\KimoPCManager-Verified\KimoPCManager"
$iconPath = Join-Path $currentDir "assets\icon.ico"

$shortcut = $wsh.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $targetExe
$shortcut.WorkingDirectory = $workingDir
$shortcut.IconLocation = "$iconPath,0"
$shortcut.Description = "Kimo PC Manager"
$shortcut.Save()

$desktop = [Environment]::GetFolderPath("Desktop")
$desktopShortcutPath = Join-Path $desktop "Kimo PC Manager.lnk"
$desktopShortcut = $wsh.CreateShortcut($desktopShortcutPath)
$desktopShortcut.TargetPath = $targetExe
$desktopShortcut.WorkingDirectory = $workingDir
$desktopShortcut.IconLocation = "$iconPath,0"
$desktopShortcut.Description = "Kimo PC Manager"
$desktopShortcut.Save()

Write-Host "SUCCESS: Shortcuts created."
