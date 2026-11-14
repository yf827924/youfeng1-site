@echo off
title Tencent Cloud COS + CDN 配置向导
setlocal

echo ============================================================
echo   腾讯云 COS + CDN 配置向导
echo   youfeng1.com 搬家用
echo ============================================================
echo.

REM ---- 检查 coscmd ----
for /f "delims=" %%i in ('where coscmd 2^>nul') do set "COSCMD=%%i"
if not defined COSCMD (
  echo [1/5] coscmd 未安装，正在安装...
  pip install coscmd -q
  for /f "delims=" %%i in ('where coscmd 2^>nul') do set "COSCMD=%%i"
)
if not defined COSCMD (
  echo [ERROR] coscmd 安装失败，请手动运行: pip install coscmd
  pause
  exit /b 1
)
echo [1/5] coscmd 已就绪: %COSCMD%
echo.

REM ---- 检查 .coscfg ----
set COSCFG=%~dp0.coscfg
if exist "%COSCFG%" (
  echo [2/5] .coscfg 已存在:
  type "%COSCFG%"
  echo.
  set /p "override=要重新配置吗？y/n: "
  if /i not "!override!"=="y" goto :cdn_setup
)

:config_cos
echo [2/5] 请打开腾讯云控制台，获取以下信息：
echo.
echo   1. 访问管理 https://console.cloud.tencent.com/cam/capi
echo      -> 创建 SecretId + SecretKey
echo   2. COS 控制台 https://console.cloud.tencent.com/cos5/bucket
echo      -> 记下桶名和区域（如 ap-shanghai）
echo   3. 启用静态网站托管，记下访问域名
echo.
set /p "SECRET_ID=SecretId: "
set /p "SECRET_KEY=SecretKey: "
set /p "REGION=区域（如 ap-shanghai）: "
set /p "BUCKET=桶名: "
set /p "PREFIX=上传前缀（如 youfeng1.com/）: "

echo [secret_id=%SECRET_ID%] > "%COSCFG%"
echo [cos] >> "%COSCFG%"
echo secret_id = %SECRET_ID% >> "%COSCFG%"
echo secret_key = %SECRET_KEY% >> "%COSCFG%"
echo region = %REGION% >> "%COSCFG%"
echo bucket = %BUCKET% >> "%COSCFG%"
echo prefix = %PREFIX% >> "%COSCFG%"

echo [3/5] coscfg 已写入:
type "%COSCFG%"
echo.

:cdn_setup
echo [4/5] CDN 配置（需手动操作）：
echo.
echo   1. 打开 CDN 控制台: https://console.cloud.tencent.com/cdn
echo   2. 添加加速域名: youfeng1.com
echo   3. 回源类型: 域名
echo   4. 回源域名: 填 COS 静态网站域名
echo      (格式: your-bucket.cos-website.ap-shanghai.myqcloud.com)
echo   5. SSL: 申请免费证书
echo   6. 缓存规则: HTML 设 300s, 静态资源设 7天
echo.
echo   CDN 加速域名会是: youfeng1.com.pub.min.tc.com
echo   （最后用 CNAME 指向这个地址）
echo.

set /p "CDN_DOMAIN=CDN 加速域名（回填用于 DNS）: "
if defined CDN_DOMAIN (
  echo [5/5] DNS 切换指引：
  echo.
  echo   Cloudflare -> youfeng1.com -> 修改 A 记录 -> 指向 %CDN_DOMAIN%
  echo   Cloudflare -> www.youfeng1.com -> CNAME -> %CDN_DOMAIN%
  echo.
  echo   注意: Cloudflare 的 DNS 代理（橙色云）要关闭，
  echo        否则 CDN 回源会被 Cloudflare 拦截。
  echo        你feng1.com 当前是灰云（仅 DNS），保持不变即可。
  echo.
)

echo ============================================================
echo   配置完成！
echo   以后发布: 双击 publish_cos.bat
echo ============================================================
pause
