@echo off
chcp 936 >nul 2>nul
setlocal
cd /d "%~dp0"
title 同步小说并发布 youfeng1.com

REM 找一个可用的 python（系统没装就用 WorkBuddy 自带的）
set "PYEXE="
for /f "delims=" %%i in ('where python 2^>nul') do if not defined PYEXE set "PYEXE=%%i"
if not defined PYEXE (
  for /d %%d in ("%USERPROFILE%\.workbuddy\binaries\python\versions\*") do (
    if not defined PYEXE if exist "%%d\python.exe" set "PYEXE=%%d\python.exe"
  )
)
if not defined PYEXE (
  echo [错误] 没有找到 python（需要 WorkBuddy 自带的 python）。
  echo.
  pause
  exit /b 1
)

"%PYEXE%" "%~dp0..\.deploy\sync_publish.py" %*

echo.
pause
