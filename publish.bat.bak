@echo off
chcp 936 >nul 2>nul
setlocal
cd /d "%~dp0"
title 一键发布 youfeng1.com

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

REM 把 git 自带目录放进 PATH，让 git 用 PortableGit 的 ssh
for %%i in ("%GITEXE%") do set "GITDIR=%%~dpi"
set "PATH=%GITDIR%;%GITDIR%..\mingw64\bin;%GITDIR%..\usr\bin;%PATH%"

REM 发布密钥（正斜杠，反斜杠会被 git 吃掉）
"%GITEXE%" config core.sshCommand "ssh -i C:/Users/user/WorkBuddy/2026-09-18-23-23-45/projects/.deploy/id_ed25519 -o StrictHostKeyChecking=accept-new -o UserKnownHostsFile=C:/Users/user/WorkBuddy/2026-09-18-23-23-45/projects/.deploy/known_hosts -o BatchMode=yes"

REM 自我修复远程跟踪关系（防止 push 时报 upstream gone）
"%GITEXE%" config remote.origin.url git@github.com:yf827924/youfeng1-site.git
"%GITEXE%" config remote.origin.fetch "+refs/heads/*:refs/remotes/origin/*"
"%GITEXE%" config branch.main.remote origin
"%GITEXE%" config branch.main.merge refs/heads/main
"%GITEXE%" config push.default simple

echo [环境] git = %GITEXE%
echo [环境] 站点 = %CD%
echo.

REM ---------- 2) 本次提交说明（默认纯英文，避免中文乱码） ----------
if "%~1"=="" (set "MSG=site update") else (set "MSG=%~1")

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
"%GITEXE%" push origin main
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
