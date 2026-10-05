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

双击它，会自动完成四步：
1. **环境自检**：确认 `CNAME`、发布私钥、`publish.bat` 都在（缺了立刻报警，不会默默失败）
2. **找源站**：在 `D:\workbuddy\2026-09-02-08-41-25\` 下的几个作品小屋目录里，自动挑**章节最多、最新**的那个（当前是 `portfolio`）
3. **只同步有差异的文件**：新增章节 + 更新过的页面 + 配套音频，保留文件不动
4. **调用 `publish.bat` 推送到 GitHub**

- 屏幕第一行会打印 `[环境] python = ...`，并明确列出「源站 / 当前站」各多少章 —— **看一眼章数就知道同步有没有生效**
- 源站没有更新时，会明确说「本地与源站内容完全一致」，然后**照样推送一次**（无害，保证线上是最新）
- 全程日志写在 `D:\workbuddy\2026-09-11-10-33-06\.deploy\last_run.log`，出问题直接把窗口内容或这个文件发给助手
- **不会被覆盖删除**：`.git`、`.gitignore`、`CNAME`、`publish.bat`、`同步小说并发布.bat`、`README_发布指南.md`

> 如果小说源站换到了别的目录，告诉助手改一下 `D:\workbuddy\2026-09-11-10-33-06\.deploy\sync_publish.py` 里的路径。

### ⚠️ 为什么需要这个脚本（踩过的坑）

小说源站会**整体重新生成**（不是只加新章节），所以手工拷贝容易出现两种错：
- **拷贝时机太早**：源站还没更新，拷到的是旧版（本项目就踩过：源站已 90 章，站上还是 75 章）
- **只拷新增章节**：1~75 章本身也被重新生成过，只补 76~90 会漏掉前面的更新

所以固定用「**与源站做全量差异比对，再增量同步**」的做法，不要凭感觉拷文件。

---

## 一之三、桌面上的快捷入口（2026-09-12 加）

桌面上现在有两个双击入口，不用再进 D 盘目录：

| 桌面文件 | 作用 |
|---|---|
| **`同步小说并发布.bat`** | 小说更新后用：自动找源站 → 增量同步章节和音频 → 发布 |
| **`一键发布.bat`** | 改了站里其它内容（首页、文章、游戏等）后用：直接提交 + 推送 |

它们是**转发入口**，不是原文件的副本 —— 内容里 `call` 到 `hugo-site` 下的主脚本，
所以以后主脚本更新了，桌面双击到的**自动就是最新版**，不会出现两份不同步的问题。

- 主脚本位置：`D:\workbuddy\2026-09-11-10-33-06\hugo-site\`
- 想重建桌面入口（比如误删了、或换了电脑）：跑 `.deploy\gen_desktop_bats.py`
- 读的时候别用记事本乱改，会破坏 GBK 编码 → 用记事本打开后**直接保存**就会坏，需要重建

> ⚠️ 桌面入口能用的前提是 `D:\workbuddy\2026-09-11-10-33-06\` 这个目录还在原位。
> 如果哪天要挪整个项目目录，记得先告诉我，重新生成桌面的转发路径。

---

## 二、当前的架构（已经配好，不用再动）

| 部分 | 现在的情况 |
|---|---|
| 域名 | `youfeng1.com` 注册在 **Cloudflare**，你本人名下，随时可转出 |
| 托管 | **GitHub Pages**（免费），仓库 `yf827924/youfeng1-site`（公开，分支 `main`） |
| 内容 | 全站 273MB / 333 文件，含 **95 章小说**（每章配 1 集音频，共 95 集）、小游戏、文章、旅行影像、镖局 APK |
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

**症状：双击 `同步小说并发布.bat` 后，章节数没变 / 好像什么都没干**
1. 看窗口第一行有没有 `[环境] python = ...`
   - **没有** → 说明 python 没找到，窗口里会有 `[错误] 没有找到可用的 python`
   - 有，但指向 `...\WindowsApps\python.exe` → 这是**假 python**（微软商店的占位程序），见下方「踩坑记录」第 4 条
2. 看窗口里打印的「源站 X 章 / 当前站 Y 章」
   - 两者**相同** → 源站确实没更新，属于正常（脚本仍会推一次）
   - 源站**大于**当前站 → 应该会同步，若报错就把窗口内容发给助手
3. 都正常但网站上没变 → 等 2 分钟 + `Ctrl + F5` 强制刷新

**症状：窗口里中文变成一堆乱字符（2026-09-12 已修）**
- 这是**脚本自己的输出编码写错了**，不是电脑的问题，也不影响发布结果（内容照样推上去了）
- 原因见文末「踩坑记录」第 5 条：Python 在 Windows 控制台本该用宽字符直接写屏幕，中文天生正确；一旦强行把输出编码改成 GBK，就会在窗口里变成乱字符
- 顺带把启动器自己的提示改成了 ASCII（`[ENV] python = ...`），这样即使 `chcp` 失效也不会花屏 —— **窗口里的中文说明全部由 Python 输出**

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

### 4. `where python` 找到的可能是"假 python"（2026-09-12 踩）

Windows 自带一个**应用商店占位程序**：

```
C:\Users\16668\AppData\Local\Microsoft\WindowsApps\python.exe
   → 实际指向 AppInstallerPythonRedirector.exe（不是真 python）
```

它在系统 PATH 里，所以双击 `.bat` 时（那时 PATH 是系统 PATH，不含 WorkBuddy 的目录）`where python` **会先找到它**。
老版本的 `同步小说并发布.bat` 就这样踩坑：拿到假 python → 脚本压根没执行 → 双击后"什么都没发生"。

正确写法（已用在现行 `同步小说并发布.bat` 里）：

```bat
REM 1) 优先 WorkBuddy 自带 python
for /d %%d in ("%USERPROFILE%\.workbuddy\binaries\python\versions\*") do (
  if not defined PYEXE if exist "%%d\python.exe" set "PYEXE=%%d\python.exe"
)
REM 2) 再退回系统 python，且必须排除 WindowsApps 占位程序
if not defined PYEXE (
  for /f "delims=" %%i in ('where python 2^>nul') do (
    if not defined PYEXE (
      echo %%i | find /i "WindowsApps" >nul || set "PYEXE=%%i"
    )
  )
)
```

> 顺带解释：`publish.bat` 一直没事，是因为它找的是 `git` —— 你电脑没装 Git，`where git` 找不到，于是正常退回到 WorkBuddy 自带的 PortableGit。而 python 这边"找得到假货"，所以没走退回分支。

生成 `同步小说并发布.bat` 的脚本是 `.deploy\gen_sync_bat.py`，改完跑一下即可。

### 5. 别给 Python 的 stdout 乱设编码（2026-09-12 踩）

出错写法（会让窗口刷满乱字符）：

```python
sys.stdout.reconfigure(encoding='gbk', errors='replace')   # ❌ 无条件这么写是错的
```

原因：Python 3.6+ 在 Windows 控制台底下用的是 `_WindowsConsoleIO`（PEP 528），
**它接收的是 UTF-8 字节**，再转成 UTF-16 调 `WriteConsoleW` 显示。
所以控制台里的中文本来就天生正确，跟 `chcp` 是 936 还是 65001 **无关**。

一旦把编码强行改成 GBK，「中」会被编成 `D6 D0`，但收到字节的那一端仍按 **UTF-8** 去解
→ 窗口里就是一堆 `ÖÐ` 之类的乱字符。

正确写法：

```python
import sys
if not sys.stdout.isatty():          # 只有被别的程序用管道捕获时
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
# 控制台（双击）时什么都不做 —— 让 Python 自己走宽字符 API
```

配套经验：**启动器 .bat 自己的提示语尽量用 ASCII**（`[ENV]`、`[ERROR]` 而不是中文），
把中文提示全部交给 Python 输出 —— 这样即使某台机器 `chcp` 没生效，窗口也不会花屏。
