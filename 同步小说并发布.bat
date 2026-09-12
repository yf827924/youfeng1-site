@echo off
chcp 936 >nul 2>nul
setlocal
cd /d "%~dp0"
REM 标题/提示刻意用 ASCII：万一 chcp 没生效也不会花屏，中文提示交给 python 输出
title Sync and Publish - youfeng1.com

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
  echo [ERROR] python not found.
  echo         Need: %USERPROFILE%\.workbuddy\binaries\python\versions\*\python.exe
  echo.
  pause
  exit /b 1
)

echo [ENV] python = %PYEXE%
echo.

"%PYEXE%" "%~dp0..\.deploy\sync_publish.py" %*
set "RC=%ERRORLEVEL%"

echo.
if not "%RC%"=="0" echo [NOTE] exit code = %RC%  (send the screen above to the assistant)
pause
exit /b %RC%
