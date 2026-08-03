# 视觉风格

**视觉必须服务于内容任务。** 按这些维度挑 2–3 个方向给用户：行业与受众预期 / 作品是否依赖图像 / 内容密度与更新频率 / 用户想呈现的性格 / 现有品牌资产 / 无障碍与性能约束。

每个方向都要说明：字体气质、配色、布局密度、图像策略、组件形态、交互节奏，以及**为什么适合这个用户**。

**用户给了参考网址、截图或设计规范时，先读 [style-extraction.md](style-extraction.md)**——那里讲怎么把参考物变成下面这套变量，本文件的六种风格是「用户没有参考物」时的备选。

改风格 = 改 `assets/starter/site.css` 里 `:root` 和 `:root[data-theme="dark"]` 的变量 + 少量字号/圆角。**不要重写整个 CSS 文件。**

可调的变量：`--bg --text --muted --light --fill --fill-strong --link-underline --code-bg --invert-bg --invert-text --max --sans`

---

## 1 · 极简黑白（Minimal Mono）

黑白灰 + 大留白，靠间距分区不画线。安全牌，任何站型都不出错，中文尤其耐看。
参考：jerryzhang.me、read.cv、大多数开发者个人页。

```css
--bg:#fafbfc; --text:#0c0d10; --muted:#5e5f66; --light:#8a8b90; --max:760px;
--sans:"Inter",ui-sans-serif,-apple-system,"PingFang SC",sans-serif;
/* dark */ --bg:#000; --text:#f2f2f3; --muted:#9a9a9e;
```
字号 17px / 行高 1.75 / h1 40px / 圆角 8px。适合：A C D E F。

## 2 · 编辑排版（Editorial Serif）

衬线正文 + 窄栏 + 首字下沉，像一本书。文字量大的站最好看。
参考：个人博客、Newsletter 作者页、Medium 早期。

```css
--bg:#fdfcfa; --text:#1a1815; --muted:#6b6660; --max:680px;
--sans:"Source Serif 4",Georgia,"Songti SC",serif;
/* 强调色 */ --accent:#8b3a2f;
```
字号 19px / 行高 1.8 / h1 44px 常规字重 / 圆角 2px。适合：C D。

## 3 · 终端极客（Terminal）

等宽字体 + 深色底 + 绿/琥珀强调 + ASCII 分隔线。个性强，非技术受众慎用。
参考：dotfiles 风个人页、hacker 主页。

```css
--bg:#0d1117; --text:#c9d1d9; --muted:#8b949e; --accent:#3fb950; --max:820px;
--sans:"JetBrains Mono","SF Mono",ui-monospace,monospace;
```
字号 15px / 行高 1.7 / 标题用 `## ` 前缀 / 圆角 0。适合：F D（技术向 A）。

## 4 · 卡片仪表盘（Bento Grid）

网格卡片，每张卡一个模块（数据、产品、社交、Now），信息密度高、一屏看完全部。
参考：Apple 官网 bento 区、personal dashboard 风个人站。

```css
--bg:#f4f4f5; --text:#18181b; --muted:#71717a; --fill:#fff; --max:1080px;
--sans:"Inter",-apple-system,"PingFang SC",sans-serif;
```
卡片：白底 / 圆角 20px / 阴影 `0 1px 3px rgba(0,0,0,.06)` / grid `repeat(auto-fit,minmax(260px,1fr))`。适合：E F。

## 5 · 杂志大标题（Editorial Display）

超大字号标题（clamp 到 96px）、强对比、大图铺满。视觉冲击强，适合作品驱动。
参考：设计师作品集、Awwwards 类站点。

```css
--bg:#111; --text:#fff; --muted:#a1a1aa; --accent:#ff4d00; --max:1200px;
--sans:"Archivo","Helvetica Neue","PingFang SC",sans-serif;
```
h1 `clamp(48px,9vw,120px)` / 字重 800 / `letter-spacing:-0.03em` / 图片占满视口宽。适合：B。

## 6 · 暖色手作（Warm Handmade）

米色/奶油底 + 手写感标题 + 圆角大 + 细描边。亲和力强，去技术感。
参考：个人博客、生活记录站、独立创作者页。

```css
--bg:#fbf7f0; --text:#33302b; --muted:#7a7368; --fill:#f2ece1; --accent:#c4703f; --max:720px;
--sans:"Nunito","PingFang SC",sans-serif;
```
圆角 16px / 描边 `1px solid rgba(0,0,0,.08)` / h1 36px。适合：C D。

---

## 对标品牌风格

用户说「做成 Notion 的感觉」「Apple 风」「Vercel 那种」「Claude 风」，或希望通过品牌来选风格时：

1. 调用 **brand-design-md** skill，它会 `npx getdesign@latest add <slug>` 拉取该品牌的 DESIGN.md（60+ 品牌，含 apple / notion / claude / vercel / stripe / linear / figma / raycast / supabase 等）。
2. 识别品牌名称与主次关系（混搭时谁是主）。
3. 从 DESIGN.md 取：主色与中性色阶、字体栈、圆角、阴影、间距节奏。
4. 映射到已确认的信息架构和 `site.css` 的 `:root` 变量（亮/暗都要映射）。**取气质，不复制品牌的文案、Logo 和受保护资产**，也别整套照搬它的组件。
5. 保留人物和内容本身的独特性——网站的主角是用户，不是那个品牌。

**推荐映射：**

| 品牌 | 适合 |
|---|---|
| Notion | 编辑台气质、知识型个人站、写作者 |
| Apple | 高质量人物或作品影像 + 克制界面 |
| Linear / Vercel | 开发者、AI Builder、独立产品人 |
| Stripe | 产品、技术商业、咨询获客 |
| Airbnb | 人物、社区与服务 |
| Nike | 运动、影像、强个人表达 |

## 平台参考（只借鉴，不生成）

用户提到这些平台时，把它们当**结构和气质参考**：

- **WordPress** — 成熟的简历 / 作品 / 博客 / 分类结构，适合研究内容模块和长期维护方式
- **Framer** — 强首屏、作品动效、视觉节奏，适合作品集与创作者
- **Webflow** — 案例网格、CMS 分类、营销转化结构，适合自由职业与咨询
- **Notion** — 清晰层级、内容密度、轻量维护，适合写作者与知识工作者

**除非用户明确要求，不生成 WordPress 主题、Framer 项目或 Webflow 项目**，也不要假装能导出成这些平台的格式。

## 图像与动效

- 优先使用本人照片、真实作品、产品截图和过程材料
- 人物照片需确认使用许可和裁切偏好
- 生成的图片必须标注为生成素材，**不能伪造客户项目或活动现场**
- 动效只用于解释层级、切换状态或强化作品，不遮挡阅读；支持 `prefers-reduced-motion`
- 不用无关渐变、漂浮色块、模板化装饰来填补空白——空白本身是设计

## 选风格时怎么问用户

给 2–3 个带理由的推荐，不要罗列全部。例：

> 你的内容以长文和记录为主，我推荐两种：
> 1. **编辑排版** — 衬线窄栏，长文最耐读，缺点是不够「科技感」
> 2. **极简黑白** — 最安全，中英混排都干净，也最容易日后改
> 或者你有想对标的产品/网站，告诉我品牌名，我按它的设计规范来做。

## 通用视觉约束（任何风格都要守）

- 亮/暗双主题都要可读，对比度 ≥ 4.5:1
- 字体不超过 2 种，字号层级不超过 5 级
- 动画只用于状态反馈（hover / 主题切换），不做入场动画堆砌
- 中文行高 ≥ 1.7，段间距 ≥ 18px
- 移动端：容器 `max-width` + 相对单位，宽内容自己 `overflow-x:auto`
