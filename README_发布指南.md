# 发布指南 · 雨果的作品小屋（youfeng1.com）

> 站点已经上线，这份文档只讲**以后怎么改内容、怎么发布、出问题怎么查**。

---

## 一、以后怎么发布（就一件事）

改完 `hugo-site/` 里任何文件（加章节、改文案、换图都行）→ **双击 `publish.bat`** → 完成。

脚本会自动：`git add` → `commit` → `push` → GitHub Pages 自动重新部署 → 1~2 分钟后 `https://youfeng1.com` 就是新的。

- 想写提交说明：`publish.bat "新增第76章"`（不加则自动用日期时间）
- **不需要你电脑装 Git**：脚本会自动找 WorkBuddy 自带的 Git，找不到才提示你去装

---

## 二、当前的架构（已经配好，不用再动）

| 部分 | 现在的情况 |
|---|---|
| 域名 | `youfeng1.com` 注册在 **Cloudflare**，你本人名下，随时可转出 |
| 托管 | **GitHub Pages**（免费），仓库 `yf827924/youfeng1-site`（公开，分支 `main`） |
| 内容 | 全站 254MB / 300+ 文件，含 75 章小说、小游戏、文章、旅行影像、镖局 APK |
| HTTPS | Let's Encrypt 证书已签发，`http://` 自动 301 跳到 `https://` |
| DNS | 根域 `youfeng1.com` → GitHub 的 4 条 A + 4 条 AAAA；`www` → CNAME `yf827924.github.io`（两条都必须是**灰云 / 仅 DNS**，不能开橙色云代理） |

DNS 原理：域名解析直接指向 GitHub 的服务器，Cloudflare 只做 DNS 解析、不参与流量，这样 GitHub 才能签证书。

---

## 三、⚠️ 两件千万不要做的事

1. **不要在 GitHub 网页的 Pages 设置里点 `Remove`（删除自定义域）**
   这会连带删掉仓库里的 `CNAME` 文件，导致 `youfeng1.com` 直接变成 404。
   （已经踩过一次，靠重新推送 `CNAME` 文件救回来了。）

2. **不要删这两个文件夹/文件**
   - `D:\workbuddy\2026-09-11-10-33-06\.deploy\` —— 发布用的 SSH 私钥，删了就无法推送
   - `hugo-site\CNAME` —— 内容是 `youfeng1.com`，删了域名会掉

---

## 四、出问题怎么查（按顺序看）

**症状：`youfeng1.com` 打不开 / 显示 404 "Site not found"**
1. 先看 `hugo-site\CNAME` 文件在不在、内容是不是 `youfeng1.com`
2. 不在就新建一个，内容填 `youfeng1.com`，然后双击 `publish.bat` 推上去
3. 若还不行，备用地址一定通：`https://yf827924.github.io/youfeng1-site/`

**症状：改了内容但网站上没变**
1. 等 2 分钟（GitHub 部署有延迟）
2. 浏览器强制刷新 `Ctrl + F5`
3. 打开 https://github.com/yf827924/youfeng1-site/commits/main 看是否有你刚才的提交

**症状：双击 publish.bat 一闪而过或报错**
1. 对着 `publish.bat` 右键 → 以管理员身份运行，再试
2. 截图报错信息给助手

**症状：GitHub 网页打不开**
不影响发布，双击 `publish.bat` 照样能推。也可以换网络（手机热点）或换 DNS（改成 `223.5.5.5`）后再试。

---

## 五、文件结构

```
hugo-site/
├── index.html            首页（作品小屋四板块入口）
├── novels/               小说章节
├── games/                小游戏
├── articles/             文章
├── videos/               旅行影像
├── downloads/            镖局 APK
├── assets/               样式/脚本/图片
├── CNAME                 ★ 绑定域名用，内容必须是 youfeng1.com
├── publish.bat           ★ 一键发布脚本
└── README_发布指南.md    本文件
```

## 六、其它

- 单个文件 ≤ **100MB**（GitHub Pages 限制），当前最大 93M，安全
- 仓库总量 254MB，远低于 GitHub 1GB 软上限，无需 Git LFS
- 换电脑：把 `hugo-site` **和** `.deploy` 两个文件夹一起拷过去，双击 `publish.bat` 照样能发
