# 发布指南 · 雨果的作品小屋（youfeng1.com）

> 站点已经上线，这份文档只讲**以后怎么改内容、怎么发布、出问题怎么查**。

---

## 一、以后怎么发布（就一件事）

改完 `hugo-site/` 里任何文件（加章节、改文案、换图都行）→ **双击 `publish.bat`** → 完成。

脚本会自动：`git add` → `commit` → `push` → GitHub Pages 自动重新部署 → 1~2 分钟后 `https://youfeng1.com` 就是新的。

- 想写提交说明：直接把说明拖到 `publish.bat` 上（如 `publish.bat "add chapter 76"`）；不写则自动用 `site update`
  - 说明可以是中文，GitHub 上显示正常；但**黑色命令行窗口里那行提交信息可能显示成乱码**，属正常现象，不影响发布
- **不需要你电脑装 Git**：脚本会自动找 WorkBuddy 自带的 Git，找不到才提示你去装

---

## 一之二、小说更新了怎么发（专用一键脚本）

小说章节在源站更新后，用 **`同步小说并发布.bat`**：

双击它，会自动完成三步：
1. 找到小说源站（`D:\workbuddy\2026-09-02-08-41-25\portfolio_live`，自动挑章节最多的那个）
2. 只把**有差异**的文件同步进本目录（新增章节 + 更新的页面，含配套音频），只保留必要文件不动
3. 调用 `publish.bat` 推送到 GitHub

- 源站没有更新时，它会明确告诉你「与源站内容完全一致，无需同步」，然后照样走一次发布（无害）
- **不会被覆盖删除**：`.git`、`.gitignore`、`CNAME`、`publish.bat`、`同步小说并发布.bat`、`README_发布指南.md`

> 如果小说源站换到了别的目录，告诉助手改一下 `D:\workbuddy\2026-09-11-10-33-06\.deploy\sync_publish.py` 里的路径。

### ⚠️ 为什么需要这个脚本（踩过的坑）

小说源站会**整体重新生成**（不是只加新章节），所以手工拷贝容易出现两种错：
- **拷贝时机太早**：源站还没更新，拷到的是旧版（本项目就踩过：源站已 90 章，站上还是 75 章）
- **只拷新增章节**：1~75 章本身也被重新生成过，只补 76~90 会漏掉前面的更新

所以固定用「**与源站做全量差异比对，再增量同步**」的做法，不要凭感觉拷文件。

---

## 二、当前的架构（已经配好，不用再动）

| 部分 | 现在的情况 |
|---|---|
| 域名 | `youfeng1.com` 注册在 **Cloudflare**，你本人名下，随时可转出 |
| 托管 | **GitHub Pages**（免费），仓库 `yf827924/youfeng1-site`（公开，分支 `main`） |
| 内容 | 全站 273MB / 332 文件，含 **90 章小说**（每章配 1 集音频，共 90 集）、小游戏、文章、旅行影像、镖局 APK |
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

**症状：双击 publish.bat 满屏「不是内部或外部命令，也不是可运行的程序或批处理文件」**
- 这是**批处理文件编码**问题，已修复（原因见文末「踩坑记录」）。若又出现，说明 `publish.bat` 被某个编辑器改存成了 UTF-8，告诉助手重新生成即可。

**症状：双击 publish.bat 一闪而过或报错**
1. 先确认不是上面那条编码问题
2. 对着 `publish.bat` 右键 → 以管理员身份运行，再试
3. 截图报错信息给助手

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

---

## 七、踩坑记录（写给以后的自己）

`publish.bat` 这种**含中文的 Windows 批处理文件**，有三个必须同时满足的硬条件，缺一个就满屏报错：

| 要求 | 不对会怎样 |
|---|---|
| **GBK 编码**（不是 UTF-8） | cmd 默认按 GBK 读文件，UTF-8 的中文变乱码字节 → 每行都被当成命令，报「不是内部或外部命令」 |
| **CRLF 换行**（不是 Unix 的 LF） | cmd 逐行读取时偏移错乱，把文件内容错位当成命令执行 |
| **ssh 路径用正斜杠** | git 解析 `GIT_SSH_COMMAND` 时会吃掉反斜杠，路径变成 `C:Users16668...` → 找不到 ssh |

另外两条经验：
- **不要用 `chcp 65001` 配 GBK 中文**：这是最经典的翻车组合，改用 `chcp 936`
- **脚本里 push 写成 `git push origin main`**（而不是裸 `git push`），并每次运行自动重设 `branch.main.merge`——这样即使远程跟踪引用丢失（`git status` 显示 `[gone]`），也永远不会推不上去

重新生成这个文件的脚本在 `D:\workbuddy\2026-09-11-10-33-06\.deploy\gen_bat.py`，改完跑一下就会输出正确编码的 `publish.bat`。
