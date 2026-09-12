@echo off
chcp 65001 >nul 2>nul
setlocal
REM ============================================================
REM  一键发布  ——  改完网页/内容后，双击本文件即可上线
REM  用法：  publish.bat "本次更新的说明"   （说明可省略）
REM  发布目标： https://youfeng1.com
REM  原理：把本目录内容提交并推送到 GitHub，GitHub Pages 会自动重新部署
REM ============================================================
cd /d "%~dp0"

REM ---------- 1) 找一个可用的 git ----------
set "GITEXE="
for /f "delims=" %%i in ('where git 2^>nul') do if not defined GITEXE set "GITEXE=%%i"

if not defined GITEXE (
  for /f "delims=" %%i in ('dir /b /s "%USERPROFILE%\.workbuddy\binaries\PortableGit\versions\*\cmd\git.exe" 2^>nul') do if not defined GITEXE set "GITEXE=%%i"
)

if not defined GITEXE (
  echo.
  echo [错误] 没有找到 git。
  echo        请安装 Git for Windows: https://git-scm.com/download/win
  echo.
  pause
  exit /b 1
)
echo 使用 git: %GITEXE%

REM ---------- 2) 让 git 使用自带的 ssh（系统 ssh 会拒绝本仓库的私钥） ----------
for %%i in ("%GITEXE%") do set "GITBIN=%%~dpi"
set "PATH=%GITBIN%;%GITBIN%..\mingw64\bin;%GITBIN%..\usr\bin;%PATH%"

REM ---------- 3) 提交说明 ----------
if "%~1"=="" (set "MSG=更新 %date% %time%") else (set "MSG=%~1")

REM ---------- 4) 提交 ----------
"%GITEXE%" add -A
"%GITEXE%" diff --cached --quiet
if errorlevel 1 (
  "%GITEXE%" commit -m "%MSG%"
  echo [1/2] 已提交本次改动
) else (
  echo [1/2] 没有新改动，跳过提交
)

REM ---------- 5) 推送 ----------
echo [2/2] 正在推送到 GitHub ...
"%GITEXE%" push
if errorlevel 1 (
  echo.
  echo [失败] 推送没有成功。把上面的报错信息发给助手。
) else (
  echo.
  echo ============================================================
  echo  发布完成！等 1-2 分钟，打开 https://youfeng1.com 查看。
  echo ============================================================
)

echo.
pause
