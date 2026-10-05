> ⚠️ **已废弃（2026-10-05）** —— 本方案卡在 **ICP 备案**：腾讯云中国大陆的存储桶和 CDN，绑定自定义域名必须通过工信部备案。改用 **Cloudflare R2**，见 **`MIGRATE_R2.md`**。本文件仅作历史记录保留。

# youfeng1.com 搬家指南（GitHub Pages -> 腾讯云 COS+CDN）

> 生成时间：2026-10-05
> 现状：GitHub Pages + Cloudflare DNS
> 目标：腾讯云 COS 静态托管 + CDN 加速 + 保留 GitHub 作备份

---

## 0. 费用预估

| 项目 | 价格 |
|---|---|
| COS 存储 | ~¥0.03/GB/月（当前 273MB ≈ ¥0.008/月） |
| COS 流量 | ~¥0.03/GB（CDN 加速后几乎不走 COS 出口） |
| CDN 加速 | ~¥0.03/GB（国内流量，前 1TB 有免费额） |
| SSL 证书 | 免费（腾讯云自动申请） |
| **合计** | **~¥3-8/月**（新用户首月可能免费） |

---

## 1. 开通 COS + CDN

### 1.1 COS 桶
1. 登录 https://console.cloud.tencent.com/cos5/bucket
2. 创建桶：`youfeng1-com`（或自命名）
3. 区域：选 **上海** 或 **广州**
4. **开启静态网站托管**
   - 索引文档：`index.html`
   - 错误文档：`404.html`
5. 记下**静态网站域名**：`youfeng1-com.cos-website.ap-shanghai.myqcloud.com`

### 1.2 CDN
1. 登录 https://console.cloud.tencent.com/cdn
2. 添加加速域名：`youfeng1.com`
3. 回源类型：**域名**
4. 回源域名：`youfeng1-com.cos-website.ap-shanghai.myqcloud.com`
5. SSL：**申请免费证书**
6. 缓存规则：
   - `*.html` -> 300s
   - `*.js,*.css,*.png,*.jpg,*.woff2` -> 7天
7. 加速范围：**国内**

记下 CDN 域名（如 `youfeng1.com.pub.min.tc.com`）

### 1.3 凭证
1. https://console.cloud.tencent.com/cam/capi
2. 创建 SecretId + SecretKey
3. 记下来（只显示一次）

---

## 2. 配置 coscmd

```bat
pip install coscmd
coscmd config -i <SecretId> -k <SecretKey> -e ap-shanghai -b youfeng1-com -p youfeng1.com/
```

测试：
```bat
coscmd ls
```

---

## 3. DNS 切换

Cloudflare 控制台 -> youfeng1.com DNS：

| 记录 | 类型 | 值 | 代理 |
|---|---|---|---|
| @ | A | CDN IP（或保留 CNAME） | 灰色云（仅 DNS） |
| www | CNAME | CDN 域名 | 灰色云 |

**注意**：Cloudflare 当前是灰云（仅 DNS），不要开橙色云（代理），否则会拦截 CDN 回源。

---

## 4. 发布脚本

新的发布脚本：`publish_cos.bat`

- 先走原有 GitHub publish.bat
- 再用 coscmd 同步 public/ 到 COS
- 一次发布，两边都更新

---

## 5. 验证

发布后：
1. 打开 https://youfeng1.com
2. 检查页面是否正常
3. 检查 HTTPS 证书是否生效
4. 检查 CDN 命中率：腾讯云 CDN 控制台 -> 监控

---

## 6. 回滚

如果出问题：
1. Cloudflare DNS 改回 GitHub A 记录
2. 或直接访问 `https://yf827924.github.io/youfeng1-site/`

GitHub 仓库不变，随时可切回。

---

## 7. 新用户优惠

腾讯云通常有新用户：
- $300+ 代金券
- COS 5GB 免费
- CDN 首月免费

去 https://cloud.tencent.com/product/cos 和 https://cloud.tencent.com/product/cdn 查看当前活动。
