@echo off
set "EXE=%~dp0laya-desktop.exe"
set "LNK=%USERPROFILE%\Desktop\laya-launch.bat"
copy /Y "%~dp0laya-launch.bat" "%LNK%" >nul 2>&1
start "" "%EXE%"
exit /b 0
