#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
youfeng1.com  ->  Cloudflare R2  增量同步脚本

用 boto3 走 R2 的 S3 兼容 API，把站点根目录同步到 R2 桶。

特点：
  * 自动推断 Content-Type（关键：不设置的话 HTML/MP4 会被浏览器当文件下载）
  * 文本类自动带 charset=utf-8（站点是中文的，避免乱码）
  * 按 (大小) 对比，只传新增/变化；--force 可强制全量重传
  * --delete 删除 R2 上本地已不存在的对象（保持镜像一致）
  * 默认排除 .git / _r2 / *.bat / *.md / *.py 等非站点文件

用法：
  python r2_sync.py                  # 预览（dry-run，不动任何东西）
  python r2_sync.py --go             # 真正上传
  python r2_sync.py --go --delete    # 上传并把云端多余对象删掉
  python r2_sync.py --go --force     # 忽略大小对比，全部重传
"""

import argparse
import configparser
import mimetypes
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import boto3
    from botocore.config import Config as BotoConfig
    from botocore.exceptions import ClientError
except ImportError:
    sys.exit("缺少 boto3，请先运行: pip install boto3")

HERE = os.path.dirname(os.path.abspath(__file__))
SITE_ROOT = os.path.dirname(HERE)          # _r2/ 的上一级 = 站点根
CONFIG_PATH = os.path.join(HERE, "r2_config.ini")

# ---------------- 排除规则 ----------------
EXCLUDE_DIRS = {".git", "_r2", "node_modules", "__pycache__", ".idea", ".vscode"}
EXCLUDE_EXTS = {".bat", ".py", ".pyc", ".md", ".bak", ".orig", ".ps1", ".ini", ".log"}
EXCLUDE_FILES = {".gitignore", ".DS_Store", "Thumbs.db", "CNAME"}

# mimetypes 认不出来的补充
EXTRA_TYPES = {
    ".apk": "application/vnd.android.package-archive",
    ".woff2": "font/woff2",
    ".woff": "font/woff",
    ".webp": "image/webp",
    ".m4a": "audio/mp4",
    ".mp3": "audio/mpeg",
    ".mp4": "video/mp4",
    ".json": "application/json",
    ".js": "application/javascript",
    ".svg": "image/svg+xml",
    ".webmanifest": "application/manifest+json",
}

TEXT_EXTS = {".html", ".htm", ".css", ".js", ".json", ".svg", ".xml", ".txt", ".webmanifest"}


def content_type_for(path):
    ext = os.path.splitext(path)[1].lower()
    ctype = EXTRA_TYPES.get(ext) or mimetypes.guess_type(path)[0] or "application/octet-stream"
    if ext in TEXT_EXTS and "charset" not in ctype:
        ctype += "; charset=utf-8"
    return ctype


def cache_control_for(path):
    """HTML 短缓存（改完能较快生效），静态资源长缓存"""
    ext = os.path.splitext(path)[1].lower()
    if ext in (".html", ".htm", ".json", ".webmanifest"):
        return "public, max-age=0, s-maxage=300, must-revalidate"
    return "public, max-age=604800, immutable"


def excluded(rel_dir, filename):
    parts = rel_dir.replace("\\", "/").split("/") if rel_dir not in ("", ".") else []
    if any(p in EXCLUDE_DIRS for p in parts):
        return True
    if filename in EXCLUDE_FILES:
        return True
    if os.path.splitext(filename)[1].lower() in EXCLUDE_EXTS:
        return True
    return False


def scan_local(root):
    """返回 {相对key: (绝对路径, 大小)}，key 用正斜杠"""
    out = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        rel_dir = os.path.relpath(dirpath, root)
        for fn in filenames:
            if excluded(rel_dir, fn):
                continue
            full = os.path.join(dirpath, fn)
            if not os.path.isfile(full):
                continue
            rel = os.path.relpath(full, root).replace("\\", "/")
            out[rel] = (full, os.path.getsize(full))
    return out


def scan_remote(client, bucket):
    out = {}
    paginator = client.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket):
        for obj in page.get("Contents", []):
            out[obj["Key"]] = obj["Size"]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--go", action="store_true", help="真正执行上传（默认只是预览）")
    ap.add_argument("--delete", action="store_true", help="删除 R2 上本地不存在的对象")
    ap.add_argument("--force", action="store_true", help="忽略大小对比，全部重传")
    ap.add_argument("--workers", type=int, default=8, help="并发线程数（默认 8）")
    args = ap.parse_args()

    if not os.path.exists(CONFIG_PATH):
        sys.exit(f"找不到配置文件: {CONFIG_PATH}\n请复制 r2_config.ini.example 为 r2_config.ini 并填写。")

    cfg = configparser.ConfigParser()
    cfg.read(CONFIG_PATH, encoding="utf-8")
    s = cfg["r2"]
    account_id = s.get("account_id", "").strip()
    bucket = s.get("bucket", "").strip()
    if not account_id or not bucket or not s.get("access_key_id", "").strip():
        sys.exit("r2_config.ini 里的 account_id / access_key_id / secret_access_key / bucket 必须填全。")

    endpoint = s.get("endpoint", f"https://{account_id}.r2.cloudflarestorage.com").strip()

    client = boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=s["access_key_id"].strip(),
        aws_secret_access_key=s["secret_access_key"].strip(),
        region_name="auto",
        config=BotoConfig(
            retries={"max_attempts": 5, "mode": "standard"},
            max_pool_connections=max(16, args.workers * 2),
        ),
    )

    print(f"站点根 : {SITE_ROOT}")
    print(f"桶     : {bucket}  @ {endpoint}")
    print()

    print("[1/4] 扫描本地文件 ...")
    local = scan_local(SITE_ROOT)
    total_bytes = sum(v[1] for v in local.values())
    print(f"      本地 {len(local)} 个文件，共 {total_bytes / 1048576:.1f} MB")

    print("[2/4] 列出 R2 已有对象 ...")
    remote = scan_remote(client, bucket)
    print(f"      云端 {len(remote)} 个对象")

    # 决定要传哪些
    to_upload = []
    for key, (full, size) in sorted(local.items()):
        if key not in remote:
            to_upload.append(key)
        elif args.force or remote[key] != size:
            to_upload.append(key)

    to_delete = sorted(set(remote) - set(local)) if args.delete else []

    up_bytes = sum(local[k][1] for k in to_upload)
    print()
    print(f"[3/4] 待上传 {len(to_upload)} 个文件（{up_bytes / 1048576:.1f} MB）；"
          f"跳过 {len(local) - len(to_upload)} 个；待删除 {len(to_delete)} 个")
    if to_upload[:10]:
        for k in to_upload[:10]:
            print(f"        + {k}")
        if len(to_upload) > 10:
            print(f"        ... 其余 {len(to_upload) - 10} 个")

    if not args.go:
        print()
        print("[4/4] 这是预览模式，什么也没做。确认无误后加 --go 执行。")
        return

    print()
    print(f"[4/4] 开始上传（{args.workers} 并发）...")
    done = 0
    failed = []

    def put(key):
        full, _ = local[key]
        client.upload_file(
            full, bucket, key,
            ExtraArgs={
                "ContentType": content_type_for(key),
                "CacheControl": cache_control_for(key),
            },
        )
        return key

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(put, k): k for k in to_upload}
        for fut in as_completed(futures):
            key = futures[fut]
            try:
                fut.result()
                done += 1
                if done % 50 == 0 or done == len(to_upload):
                    print(f"      已上传 {done}/{len(to_upload)}")
            except Exception as e:
                failed.append((key, str(e)))
                print(f"      [失败] {key} -> {e}")

    if to_delete:
        print(f"      删除云端多余对象 {len(to_delete)} 个 ...")
        for i in range(0, len(to_delete), 1000):
            batch = [{"Key": k} for k in to_delete[i:i + 1000]]
            client.delete_objects(Bucket=bucket, Delete={"Objects": batch, "Quiet": True})

    print()
    print("=" * 60)
    print(f"  完成：成功 {done}，失败 {len(failed)}，删除 {len(to_delete)}")
    if failed:
        print("  失败清单：")
        for k, e in failed[:20]:
            print(f"    {k} -> {e}")
    print("=" * 60)


if __name__ == "__main__":
    main()
