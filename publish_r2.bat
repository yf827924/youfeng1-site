@echo off
chcp 65001 >nul
title Publish youfeng1.com  -^>  GitHub + Cloudflare R2
setlocal

set "PY=C:\Users\user\.workbuddy\binaries\python\envs\default\Scripts\python.exe"
set "SYNC=%~dp0_r2\r2_sync.py"

echo ============================================================
echo   Publish  --  youfeng1.com
echo   1) GitHub Pages（保留作备份）
echo   2) Cloudflare R2（线上主站）
echo ============================================================
echo.

REM ---------- 1) 原有 GitHub Pages 发布 ----------
echo [1/2] 发布到 GitHub Pages ...
echo.
call "%~dp0publish.bat" %*

if not exist "%PY%" (
  echo [R2] ERROR: 找不到 python: %PY%
  pause
  exit /b 1
)
if not exist "%SYNC%" (
  echo [R2] ERROR: 找不到同步脚本: %SYNC%
  pause
  exit /b 1
)

REM ---------- 2) 同步到 Cloudflare R2 ----------
echo.
echo [2/2] 同步站点到 Cloudflare R2 ...
echo.
"%PY%" "%SYNC%" --go --delete

if errorlevel 1 (
  echo.
  echo [R2] 同步失败，请把上面的信息发给助手。
  pause
  exit /b 1
)

echo.
echo ============================================================
echo   完成！GitHub 与 R2 都已更新
echo   网站: https://youfeng1.com
echo ============================================================
echo.
pause
