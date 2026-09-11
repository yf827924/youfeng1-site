# 发布指南（youfeng1.com 作品小屋 · GitHub Pages 路线）

目标：改完网页/内容后，**双击 `publish.bat` 一条命令就上线**，不用每次去后台拖文件夹、不用每次折腾密钥。

---

## 一、你只需做 4 步（一次性，之后不用再碰）

### 第 1 步：在 GitHub 建仓库
1. 登录 https://github.com/ （没有账号先注册，免费）
2. 右上角 **＋ → New repository**
3. Repository name 填 `youfeng1-site`
4. 选 **Public**（私有仓库 GitHub Pages 要付费）
5. **不要**勾 "Add a README file" / .gitignore / license（保持空仓库）
6. 点 **Create repository**

### 第 2 步：把本机 SSH 公钥加到 GitHub
复制下面这整串（已为本机生成）：

```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIA7l7TRbDB/VyfMj7nRe5Gm/6N7xFsBnn+FixuYyS9lV youfeng1@163.com
```

1. GitHub 右上角头像 → **Settings**
2. 左侧 **SSH and GPG keys** → **New SSH key**
3. Title 随便填（如 `my-pc`），Key 框粘贴上面那串 → **Add SSH key**

> 这把密钥在本机长期有效，配一次即可，不像 Cloudflare 全局密钥那样会被建议轮换导致失效。

### 第 3 步：首次推送（把仓库地址告诉我，我帮你跑）
建好仓库后，把你的 **GitHub 用户名**发我，我会执行：
```
git remote add origin git@github.com:<你的用户名>/youfeng1-site.git
git push -u origin main
```
之后代码就上去了。

### 第 4 步：开启 Pages + 改 DNS（各点一下）
1. 进 `youfeng1-site` 仓库 → **Settings → Pages**
2. Branch 选 **main** → **Save**（等几分钟，GitHub 会给 `https://<用户名>.github.io/youfeng1-site/` 临时地址）
3. 进 Cloudflare 控制台 → `youfeng1.com` 的 **DNS**
4. 把现有的 CNAME（指向 `youfeng1-site.pages.dev`）改成指向 **`<用户名>.github.io`**
   - 根域 `youfeng1.com` → CNAME → `<用户名>.github.io`（代理保持开启）
   - `www.youfeng1.com` 同理
5. 等几分钟生效，浏览器开 **https://youfeng1.com** 就是正式站

> 域名始终注册在 Cloudflare 名下，完全独立；换主机只是改一条 CNAME，零锁定。

---

## 二、以后怎么发布（重点：一条命令）

改完 `hugo-site/` 里的任何文件（加章节、改文案、换图都行），**双击 `publish.bat`** 即可：
- 它会自动 `git add` → `commit` → `push`
- GitHub 检测到推送 → 自动重新部署到 Pages → 你的站秒级更新

可选：在双击时加说明，如 `publish.bat "新增第76章"`；不加则自动用时间戳作提交说明。

---

## 三、文件结构（当前已就绪）
```
hugo-site/
├── index.html            首页（作品小屋四板块入口）
├── novels/               75 章小说（gudo-*.html）
├── games/                小游戏
├── articles/             文章
├── videos/               旅行影像（含 93M「泰达谷的夏」）
├── downloads/            镖局 APK（29M）
├── assets/               样式/脚本/图片
├── publish.bat           ★ 一键发布脚本
└── README_发布指南.md    本文件
```

## 四、注意事项
- 单文件 ≤ 100MB（GitHub Pages 限制），当前最大 93M，安全。
- 仓库总量 254M，远低于 GitHub 1GB 软上限，无需 Git LFS。
- 若某天换电脑，把 `C:\Users\16668\.ssh\id_ed25519` 一并拷走即可继续用同一把密钥发布。
