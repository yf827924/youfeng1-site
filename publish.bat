@echo off
chcp 936 >nul 2>nul
setlocal
cd /d "%~dp0"
title 一键发布 youfeng1.com

set "KEY=D:\workbuddy\2026-09-11-10-33-06\.deploy\id_ed25519"
set "KH=D:\workbuddy\2026-09-11-10-33-06\.deploy\known_hosts"

echo ============================================================
echo   一键发布  --  youfeng1.com
echo ============================================================
echo.

REM ---------- 1) 找一个可用的 git（系统没装就用 WorkBuddy 自带的） ----------
set "GITEXE="
for /f "delims=" %%i in ('where git 2^>nul') do if not defined GITEXE set "GITEXE=%%i"
if not defined GITEXE (
  for /d %%d in ("%USERPROFILE%\.workbuddy\binaries\PortableGit\versions\*") do (
    if not defined GITEXE if exist "%%d\cmd\git.exe" set "GITEXE=%%d\cmd\git.exe"
  )
)
if not defined GITEXE (
  echo [错误] 没有找到 git。
  echo        请安装 Git for Windows: https://git-scm.com/download/win
  echo.
  pause
  exit /b 1
)
for %%i in ("%GITEXE%") do set "GITDIR=%%~dpi"
set "PATH=%GITDIR%;%GITDIR%..\mingw64\bin;%GITDIR%..\usr\bin;%PATH%"
set "GIT_SSH_COMMAND=%GITDIR%..\usr\bin\ssh.exe -i %KEY% -o StrictHostKeyChecking=accept-new -o UserKnownHostsFile=%KH% -o BatchMode=yes"
echo [环境] git = %GITEXE%
echo [环境] 站点 = %CD%
echo.

REM ---------- 2) 本次提交说明 ----------
if "%~1"=="" (set "MSG=update %date% %time%") else (set "MSG=%~1")

REM ---------- 3) 提交 ----------
"%GITEXE%" add -A
"%GITEXE%" diff --cached --quiet
if errorlevel 1 (
  "%GITEXE%" commit -m "%MSG%"
  if errorlevel 1 (
    echo.
    echo [失败] 提交出错，把上面的报错发给助手。
    echo.
    pause
    exit /b 1
  )
  echo [1/2] 已提交本次改动
) else (
  echo [1/2] 没有新改动，跳过提交
)
echo.

REM ---------- 4) 推送到 GitHub ----------
echo [2/2] 正在推送到 GitHub ...
"%GITEXE%" push
if errorlevel 1 (
  echo.
  echo [失败] 推送没成功，把上面的报错发给助手。
) else (
  echo.
  echo ============================================================
  echo   发布完成！ 等 1-2 分钟，打开 https://youfeng1.com 查看
  echo ============================================================
)
echo.
pause
