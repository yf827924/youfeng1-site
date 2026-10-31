@echo off
chcp 936 >nul 2>nul
setlocal
cd /d "%~dp0"
title Publish youfeng1.com

echo ============================================================
echo   Publish  --  youfeng1.com
echo ============================================================
echo.

REM ---------- 1) locate git (system, else bundled PortableGit) ----------
set "GITEXE="
for /f "delims=" %%i in ('where git 2^>nul') do if not defined GITEXE set "GITEXE=%%i"
if not defined GITEXE (
  for /d %%d in ("%USERPROFILE%\.workbuddy\binaries\PortableGit\versions\*") do (
    if not defined GITEXE if exist "%%d\cmd\git.exe" set "GITEXE=%%d\cmd\git.exe"
  )
)
if not defined GITEXE (
  echo [ERROR] git not found. Install Git for Windows: https://git-scm.com/download/win
  echo.
  pause
  exit /b 1
)

REM put git's own dir on PATH so git uses PortableGit's ssh
for %%i in ("%GITEXE%") do set "GITDIR=%%~dpi"
set "PATH=%GITDIR%;%GITDIR%..\mingw64\bin;%GITDIR%..\usr\bin;%PATH%"

REM deploy key (forward slashes; backslashes get eaten by git)
"%GITEXE%" config core.sshCommand "ssh -i C:/Users/user/WorkBuddy/2026-09-18-23-23-45/projects/.deploy/id_ed25519 -o StrictHostKeyChecking=accept-new -o UserKnownHostsFile=C:/Users/user/WorkBuddy/2026-09-18-23-23-45/projects/.deploy/known_hosts -o BatchMode=yes"

REM self-heal remote tracking (avoid "upstream gone" on push)
"%GITEXE%" config remote.origin.url git@github.com:yf827924/youfeng1-site.git
"%GITEXE%" config remote.origin.fetch "+refs/heads/*:refs/remotes/origin/*"
"%GITEXE%" config branch.main.remote origin
"%GITEXE%" config branch.main.merge refs/heads/main
"%GITEXE%" config push.default simple

echo [ENV] git = %GITEXE%
echo [ENV] site = %CD%
echo.

REM ---------- 2) commit message (ascii default to avoid mojibake) ----------
if "%~1"=="" (set "MSG=site update") else (set "MSG=%~1")

REM ---------- 3) squash to ONE commit each time (drops old history -> repo stays small) ----------
"%GITEXE%" add -A
"%GITEXE%" diff --cached --quiet
if errorlevel 1 (
  REM drop old history: rebuild one commit on an orphan branch, then point main to it
  "%GITEXE%" branch -D __fresh >nul 2>nul
  "%GITEXE%" checkout --orphan __fresh >nul 2>nul
  "%GITEXE%" add -A
  "%GITEXE%" commit -m "%MSG%"
  if errorlevel 1 (
    echo.
    echo [FAIL] commit failed. Send the error above to the assistant.
    echo.
    pause
    exit /b 1
  )
  "%GITEXE%" branch -M main
  echo [1/3] squashed commit created (old history dropped)
) else (
  echo [1/3] no changes, skip commit
)
echo.

REM ---------- 4) force push + shrink ----------
echo [2/3] pushing to GitHub ...
"%GITEXE%" push -f origin main
if errorlevel 1 (
  echo.
  echo [FAIL] push failed. Send the error above to the assistant.
) else (
  echo [3/3] cleaning old objects and shrinking repo ...
  "%GITEXE%" reflog expire --expire=now --all
  "%GITEXE%" gc --prune=now --aggressive
  echo.
  echo ============================================================
  echo   DONE! Wait 1-2 min, then open https://youfeng1.com
  echo ============================================================
)
echo.
pause
