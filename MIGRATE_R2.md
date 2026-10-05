# youfeng1.com 迁移到 Cloudflare R2 —— 操作指南

> 生成：2026-10-05　｜　替代 `MIGRATE_COS.md`（该方案因未备案而不可行，已废弃）
> 现状：GitHub Pages + Cloudflare DNS（灰云）　｜　目标：Cloudflare R2 + Worker

---

## 0. 为什么换方案

原方案（腾讯云 COS + 国内 CDN）**卡在 ICP 备案**：腾讯云中国大陆的桶和 CDN，绑定自定义域名必须过工信部备案，而 GitHub Pages + Cloudflare 恰恰不需要备案，所以这一步一直被忽略。

Cloudflare R2 的优势：

| 项 | 数值 |
|---|---|
| 存储 | 10 GB 免费（本站 712 MB，用掉 7%） |
| **出站流量** | **完全免费**（这是 R2 最大的卖点） |
| Worker | 免费版 10 万请求/天 |
| 自定义域名 + HTTPS | 免费，自动签发 |
| 备案 | **不需要** |
| **合计** | **¥0 / 月** |

**⚠️ 唯一前置门槛**：开通 R2 需要在 Cloudflare 账户里**添加一个付款方式**（信用卡/PayPal）。免费额度内不会扣费，但不绑卡无法开通 R2。**如果这步过不去，就先别往下做，告诉我，我们换方案。**

---

## 1. 最终架构

```
访客 → https://youfeng1.com
            │  (DNS + 自动 HTTPS，都在 Cloudflare)
            ▼
    Cloudflare Worker  youfeng1-router      ← 约 120 行，本目录 _r2/worker.js
      · /              → index.html
      · /xxx/          → xxx/index.html
      · 找不到         → 404.html
      · 视频 Range 请求 → 206（拖进度条要用）
            │  (R2 Binding，桶保持私有，不对外暴露)
            ▼
      R2 桶  youfeng1-site                   ← 1001 个文件 / 712 MB
```

**GitHub 仓库保持不动**，随时可回滚。

> 为什么不直接用「R2 公开桶 + 自定义域名」？因为 **R2 的自定义域名不会把 `/` 解析成 `/index.html`，也没有自定义 404 页**——这两个洞必须由 Worker 补。这是 R2 做静态站的标准做法。

---

## 2. 操作步骤

### 步骤 1 ｜建 R2 桶

1. 打开 https://dash.cloudflare.com → 左侧选 **R2**
2. 首次使用会要求**绑定付款方式**（免费额度内不扣费）
3. 点 **Create bucket**
4. 名称填 **`youfeng1-site`**（要和配置里的 `bucket` 完全一致）
5. Location 选 **Automatic**
6. 创建完成后，**不要**开启 Public access（保持私有，Worker 通过绑定访问）

### 步骤 2 ｜生成 API Token

1. 在 R2 页面找到 **Manage R2 API Tokens**（或右上角 API 菜单）
2. **Create API Token**
3. 权限选 **Object Read & Write**
4. 可限定范围：只勾选 `youfeng1-site` 这个桶
5. 创建后**立刻复制并保存**这三个值（Secret 只显示一次）：
   - **Access Key ID**
   - **Secret Access Key**
   - **Account ID**（这个在 R2 概览页右侧也能看到）

### 步骤 3 ｜填配置并上传

1. 进入站点目录的 `_r2\` 子目录
2. 把 `r2_config.ini.example` **复制**一份，改名为 `r2_config.ini`
3. 用记事本打开，把步骤 2 拿到的值填进去：

```ini
[r2]
account_id = 你的账号ID
access_key_id = 你的AccessKeyID
secret_access_key = 你的SecretAccessKey
bucket = youfeng1-site
endpoint =
```

4. **先预览，别急着传**。在 `_r2` 目录打开命令行跑：

```bat
C:\Users\user\.workbuddy\binaries\python\envs\default\Scripts\python.exe r2_sync.py
```

   应当看到：`本地 1001 个文件`、`云端 0 个对象`、`待上传 1001 个文件`。
   **如果"本地"数字明显不对（比如几万），先停下来告诉我。**

5. 确认无误，正式上传：

```bat
C:\Users\user\.workbuddy\binaries\python\envs\default\Scripts\python.exe r2_sync.py --go
```

   712 MB，视上行带宽约 2~20 分钟。中断了直接重跑，已传的会自动跳过。

### 步骤 4 ｜部署 Worker

1. Cloudflare 左侧 **Workers & Pages** → **Create** → **Worker** → 起名 **`youfeng1-router`** → Deploy
2. 进入 Worker → **Edit code**，把默认代码**整段删掉**，粘贴 `_r2\worker.js` 的全部内容 → **Deploy**
3. 回到 Worker → **Settings** → **Bindings**（或 Variables）→ **Add** → **R2 bucket binding**
   - Variable name 必须填 **`BUCKET`**（大小写敏感，代码里就是这个名字）
   - R2 bucket 选 **youfeng1-site**
   - 保存后**重新 Deploy 一次**

### 步骤 5 ｜先绑测试子域验证（重要，别直接切主域名）

1. Worker → **Settings** → **Domains & Routes** → **Add** → **Custom domain**
2. 填 **`test.youfeng1.com`**（域名在 Cloudflare 里，DNS 记录和证书会自动配好，约 1 分钟）
3. 逐项验证：

```bat
curl -I https://test.youfeng1.com/
curl -I https://test.youfeng1.com/novels/gudo-1.html
curl -I https://test.youfeng1.com/novels/catalog.html
curl -I -H "Range: bytes=0-1023" "https://test.youfeng1.com/videos/中秋月圆.mp4"
```

   预期：
   - 第 1 条 → `200` + `content-type: text/html; charset=utf-8`
   - 第 4 条 → **`206 Partial Content`**（不是 206 的话视频拖不动进度条）
   - 随便访问一个不存在的路径 → 应落到 404

4. **用手机/电脑浏览器实际打开 `https://test.youfeng1.com/`**，点进小说目录、听一段有声书、播一个视频。这一步不要跳过。

### 步骤 6 ｜切换到主域名

测试子域全部正常后：

1. Worker → **Domains & Routes** → **Add** → **Custom domain** → 填 **`youfeng1.com`**
2. 再加一个 **`www.youfeng1.com`**（Worker 里已写好 www→主域 的 301 跳转）
3. Cloudflare 会自动接管原指向 GitHub Pages 的 A 记录
4. 等 1~5 分钟，访问 https://youfeng1.com 确认

---

## 3. 回滚（随时可退回 GitHub Pages）

站点源码和 GitHub 仓库**全程没动过**，所以回滚只需要改 DNS：

1. Cloudflare → 你域名的 **DNS** 页面
2. 把 `youfeng1.com` 的 A 记录改回 GitHub Pages 的四个 IP：
   ```
   185.199.108.153
   185.199.109.153
   185.199.110.153
   185.199.111.153
   ```
3. `www` 改回 CNAME → `yf827924.github.io`
4. 或者：直接在 Worker 的 Domains & Routes 里**删掉自定义域名**，DNS 就交还给你手动管理

> GitHub Pages 一直在跑，最坏情况 5 分钟内可恢复。

---

## 4. 以后怎么发布新章节

双击站点目录下的 **`publish_r2.bat`** 即可，它会：

1. 先走原来的 `publish.bat` → push 到 GitHub Pages（保留备份）
2. 再用 `r2_sync.py --go --delete` 增量同步到 R2（只传变化的文件）

> `--delete` 会删掉 R2 上本地已不存在的对象，保证两处完全一致。

---

## 5. 本目录文件说明

| 文件 | 作用 |
|---|---|
| `_r2\r2_sync.py` | 上传/同步脚本（boto3 走 R2 的 S3 兼容接口） |
| `_r2\r2_config.ini.example` | 凭证配置模板，复制成 `r2_config.ini` 后填写 |
| `_r2\worker.js` | Cloudflare Worker 路由代码 |
| `publish_r2.bat` | 一键发布（GitHub + R2） |

**⚠️ `r2_config.ini` 含密钥，已加入 `.gitignore`，绝对不要提交到仓库。**

---

## 6. 成本复核

| 项 | 用量 | 费用 |
|---|---|---|
| R2 存储 | 712 MB / 10 GB 免费额度 | ¥0 |
| R2 出站流量 | 不限量 | **¥0** |
| Worker 请求 | 免费版 10 万次/天 | ¥0 |
| SSL 证书 | 自动 | ¥0 |
| **合计** | | **¥0 / 月** |

对比原腾讯云方案：国内 CDN 0.21 元/GB、中国香港 COS 流量 0.75 元/GB——**R2 在免费额度内是真正的零成本**。

---

## 7. 已修正的原方案缺陷（备查）

| 原方案问题 | 实测证据 | 现在的处理 |
|---|---|---|
| ICP 备案完全遗漏 | 用户确认未备案 | 换 R2，不需要备案 |
| `coscmd` 没有 `sync` 命令 | 1.9.0.6 实测报 `invalid choice: 'sync'` | 改用 boto3 |
| `PUBLIC_DIR=public` 不存在 | 站点根即发布目录 | 直接同步站点根 |
| `.coscfg` 是自创格式 | coscmd 读的是 `~/.cos.conf`，自创格式无效 | 用 ini + boto3 |
| `COS_PREFIX=youfeng1.com/` 路径重复 | 会变成 `youfeng1.com/youfeng1.com/index.html` | 部署到桶根 |
| 排除 `.git` 的写法不可靠 | `fnmatch` 匹配完整路径，`.git*` 会漏 | 同步脚本按目录名硬排除 |
| 站点体积写 273MB | 实际 712MB | 已更正 |
| CDN 单价写 0.03 元/GB | 实际刊例 0.21 元/GB | 已更正 |
