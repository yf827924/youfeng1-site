# -*- coding: utf-8 -*-
"""镖局本地预览服务器（带 no-cache 头）。

用法: python server_nocache.py [端口]  默认 8123
修复: Python SimpleHTTP 不发 Cache-Control，手机浏览器会强缓存旧版
index.html，导致布局修复在手机上不生效（tabs 被挡、任务书被按钮遮住）。
本脚本对所有响应加 no-cache 头，手机每次都拿最新文件。
"""
import http.server
import socketserver
import sys
from functools import partial

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8123


class NoCacheHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()


if __name__ == '__main__':
    handler = partial(NoCacheHandler, directory='.')
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(('127.0.0.1', PORT), handler) as httpd:
        print(f'serving biaoju at http://127.0.0.1:{PORT}/ (no-cache)')
        httpd.serve_forever()
