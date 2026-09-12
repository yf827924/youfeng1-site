@echo off
chcp 936 >nul 2>nul
setlocal
cd /d "%~dp0"
title 同步小说并发布 youfeng1.com

set "PYEXE="
set "PYARGS="

REM ---------- 1) 优先 WorkBuddy 自带 python ----------
for /d %%d in ("%USERPROFILE%\.workbuddy\binaries\python\versions\*") do (
  if not defined PYEXE if exist "%%d\python.exe" set "PYEXE=%%d\python.exe"
)

REM ---------- 2) 其次系统 python，但跳过 WindowsApps 商店占位程序 ----------
if not defined PYEXE (
  for /f "delims=" %%i in ('where python 2^>nul') do (
    if not defined PYEXE (
      echo %%i | find /i "WindowsApps" >nul || set "PYEXE=%%i"
    )
  )
)

if not defined PYEXE (
  echo [错误] 没有找到可用的 python。
  echo        需要 WorkBuddy 自带 python：%USERPROFILE%\.workbuddy\binaries\python
  echo.
  pause
  exit /b 1
)

echo [环境] python = %PYEXE%
echo.

"%PYEXE%" "%~dp0..\.deploy\sync_publish.py" %*
set "RC=%ERRORLEVEL%"

echo.
if not "%RC%"=="0" echo [提示] 脚本退出码 %RC%，把上面的内容发给助手。
pause
exit /b %RC%
