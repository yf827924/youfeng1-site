/**
 * youfeng1.com  ->  Cloudflare Worker + R2 静态站路由
 *
 * 为什么需要这个 Worker：
 *   R2 的自定义域名只做"按 key 取对象"，它 **不会** 把 / 映射到 /index.html，
 *   也 **没有** 自定义 404 页。静态站必须靠这层 Worker 补齐这两件事。
 *
 * 部署要点：
 *   1) 新建 Worker，整段替换默认代码
 *   2) Settings -> Bindings -> Add -> R2 bucket，变量名必须填 BUCKET，选 youfeng1-site
 *   3) Settings -> Domains & Routes -> Add Custom Domain: youfeng1.com（再单独加 www）
 *
 * 本地/线上自测：
 *   curl -I https://youfeng1.com/                # 应 200 + text/html
 *   curl -I https://youfeng1.com/novels/gudo-1.html
 *   curl -I -H "Range: bytes=0-1023" https://youfeng1.com/videos/中秋月圆.mp4   # 应 206
 */

const HTML_LIKE = /\.(html?|json|webmanifest)$/i;

function cacheControlFor(path) {
  // HTML 短缓存：改完 5 分钟内生效；静态资源长缓存
  return HTML_LIKE.test(path)
    ? 'public, max-age=0, s-maxage=300, must-revalidate'
    : 'public, max-age=604800, immutable';
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // 只放行 GET / HEAD
    if (request.method !== 'GET' && request.method !== 'HEAD') {
      return new Response('Method Not Allowed', {
        status: 405,
        headers: { Allow: 'GET, HEAD' },
      });
    }

    // www -> 主域 301
    if (url.hostname.startsWith('www.')) {
      url.hostname = url.hostname.slice(4);
      return Response.redirect(url.toString(), 301);
    }

    // 路径解码 + 去掉前导斜杠（R2 的 key 不含前导 /）
    let path = url.pathname;
    try {
      path = decodeURIComponent(path);
    } catch (e) {
      /* 解码失败就按原样用 */
    }
    path = path.replace(/^\/+/, '');

    // 目录 -> index.html
    if (path === '' || path.endsWith('/')) {
      path += 'index.html';
    }

    const rangeHeader = request.headers.get('Range');
    const getOpts = rangeHeader ? { range: request.headers } : undefined;

    let object = await env.BUCKET.get(path, getOpts);

    // 兜底 1：无扩展名的路径当成目录，试 <path>/index.html
    if (!object && !path.includes('.')) {
      object = await env.BUCKET.get(path + '/index.html', getOpts);
    }
    // 兜底 2：无扩展名，试 <path>.html
    if (!object && !path.includes('.')) {
      object = await env.BUCKET.get(path + '.html', getOpts);
    }

    // 404
    if (!object) {
      const notFound = await env.BUCKET.get('404.html');
      if (notFound) {
        return new Response(notFound.body, {
          status: 404,
          headers: { 'Content-Type': 'text/html; charset=utf-8' },
        });
      }
      return new Response('404 Not Found', {
        status: 404,
        headers: { 'Content-Type': 'text/plain; charset=utf-8' },
      });
    }

    const headers = new Headers();
    object.writeHttpMetadata(headers);          // 带出上传时写入的 Content-Type
    headers.set('etag', object.httpEtag);
    headers.set('Cache-Control', cacheControlFor(path));
    headers.set('X-Content-Type-Options', 'nosniff');
    headers.set('Accept-Ranges', 'bytes');

    // 视频拖动进度条依赖 206
    if (rangeHeader && object.range) {
      const start = object.range.offset;
      const end = object.range.offset + object.range.length - 1;
      headers.set('Content-Range', `bytes ${start}-${end}/${object.size}`);
      return new Response(request.method === 'HEAD' ? null : object.body, {
        status: 206,
        headers,
      });
    }

    return new Response(request.method === 'HEAD' ? null : object.body, {
      status: 200,
      headers,
    });
  },
};
