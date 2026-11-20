# Creates a "System Transcriber" shortcut on the desktop that opens the app window.
$dir = Split-Path -Parent $MyInvocation.MyCommand.Path
$desktop = [Environment]::GetFolderPath('Desktop')
$shell = New-Object -ComObject WScript.Shell
$link = $shell.CreateShortcut((Join-Path $desktop 'System Transcriber.lnk'))
$link.TargetPath = Join-Path $dir '.venv\Scripts\pythonw.exe'
$link.Arguments = '"' + (Join-Path $dir 'app.pyw') + '"'
$link.WorkingDirectory = $dir
$link.IconLocation = (Join-Path $dir 'icon.ico') + ',0'
$link.Description = 'Transcribe PC audio, YouTube links and files'
$link.Save()
Write-Host "Shortcut created on your desktop: System Transcriber"
