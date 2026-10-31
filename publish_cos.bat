@echo off
title Publish youfeng1.com -> GitHub + Tencent COS
setlocal enabledelayedexpansion

REM ==== 配置区（按需改） ====
set BUCKET=your-bucket-name
set REGION=ap-shanghai
set COS_PREFIX=youfeng1.com/
set PUBLIC_DIR=public

REM ==== 1. 原有 GitHub 发布流程 ====
call "%~dp0publish.bat" %*
if errorlevel 1 exit /b 1

REM ==== 2. 同步到腾讯云 COS ====
echo.
echo [COS] syncing to Tencent Cloud COS...

REM 找 coscmd
set COSCMD=
for /f "delims=" %%i in ('where coscmd 2^>nul') do if not defined COSCMD set "COSCMD=%%i"
if not defined COSCMD (
  echo [COS] coscmd not found, installing...
  pip install coscmd -q 2>nul
  for /f "delims=" %%i in ('where coscmd 2^>nul') do if not defined COSCMD set "COSCMD=%%i"
)
if not defined COSCMD (
  echo [COS] ERROR: coscmd install failed. Install manually: pip install coscmd
  pause
  exit /b 1
)

REM 确保 .coscfg 存在
if not exist "%~dp0.coscfg" (
  echo [COS] ERROR: .coscfg not found. Run coscmd config first.
  echo        coscmd config -i <SecretId> -k <SecretKey> -e %REGION% -b %BUCKET% -p %COS_PREFIX%
  pause
  exit /b 1
)

"%COSCMD%" sync -r "%~dp0%PUBLIC_DIR%\" cos://%BUCKET%/%COS_PREFIX% --delete
if errorlevel 1 (
  echo [COS] sync failed!
  pause
  exit /b 1
)

echo.
echo ============================================================
echo   DONE! GitHub + COS both updated.
echo   CDN: https://youfeng1.com
echo ============================================================
echo.
pause
