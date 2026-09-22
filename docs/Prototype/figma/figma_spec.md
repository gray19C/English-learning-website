# Figma 搭建规格文档

English Learning · MVP 低保真线框

> 本文档是给设计师在 Figma 中复刻「低保真线框原型」的搭建谱，与 `docs/Prototype/html/` 下的
> HTML 页面一一对应。设计师按本谱即可快速对齐图层、栅格、组件与状态。
> 若两者冲突，以 HTML 页面为准（HTML 是活的走查版本）。

## 1. 画板与栅格

| 项目 | 值 |
|------|----|
| 主画板（Frame） | 桌面 1440 × 900，命名 `Page_XX_名称` |
| 基线网格 | 8pt 网格；内容侧边距 48px；栅格列 12 列、gut 16px |
| 响应式断点 | 768px / 360px（原型首页第一批仅出 1440；断点于注释层标注，不做独立画板） |
| 低保真约束 | 除强调色 `#2563EB` 外全部灰阶；不用图片、不用多色；字体用系统默认 |
| 状态变体 | 同一画板内用「组件变体 / Variant」承载，命名带 `状态` 后缀 |

## 2. 样式 Token（组件属性）

### 2.1 色彩（只读 token）

| Token | 值 | 用途 |
|-------|----|------|
| `Accent` | #2563EB | 主按钮、进度条、链接、热力描边 |
| `AccentSoft` | #DBEAFE | 选中态底色 |
| `Ink` | #111827 | 正文 |
| `Gray1` | #F3F4F6 | 卡片底 / 表头底 |
| `Gray2` | #E5E7EB | 描边（卡、表、进度底） |
| `Gray3` | #D1D5DB | 虚线线框块 |
| `Gray4` | #9CA3AF | 次级文字 / 占位 |
| `Gray5` | #6B7280 | 辅助文字 |
| `Ok` | #16A34A | 答对、完成态 |
| `Warn` | #D97706 | streak、练习、积压提示 |
| `Danger` | #DC2626 | 答错态 |
| `NoteBg` | #FEF3C7 | 线框注释底色 |
| `NoteBorder` | #F59E0B | 线框注释虚线 |

### 2.2 文字（低保真用系统字体）

| Token | 字号 / 字重 | 用途 |
|-------|------------|------|
| Display | 44 / Bold | 落地页 Hero 标题 |
| H1 | 26 / Bold | 页面主标题 |
| H2 | 16-17 / Bold | 区块标题 |
| Body | 14 / Regular | 正文 |
| Caption | 12 / Regular | 注释、辅助 |
| Word | 34 / Bold | 单词卡主词 |

### 2.3 圆角 / 间距

| Token | 值 |
|-------|----|
| Radius | 8px（卡片） / 10px（选项/词卡） / 999px（标签、进度条） |
| 间距 | 8pt 基准；区块间 28px；卡片内 20px |

## 3. 组件清单（Create Components）

每个组件做成 Figma Component，后续所有页面复用。

| # | 组件名 | 说明 | 属性/Variants |
|---|--------|------|--------------|
| C01 | TopBar | 全局顶栏：品牌 + 导航 + 右侧用户胶囊 | `导航`: 今日/统计/词书/设置 |
| C02 | Footer | 全局页脚：版权 + 数据来源声明 | — |
| C03 | 断点横幅 | 顶部深色信息条（交付后删除） | — |
| C04 | Button | 按钮 | `层级`: primary/secondary/ghost；`尺寸`: md/lg；`状态`: normal/disabled |
| C05 | Card | 白底卡片 | `边框`: solid/dashed/success 描边 |
| C06 | Tag | 标签胶囊 | 色系：default/blue/green/warn |
| C07 | ProgressBar | 进度条 | 已填充百分比（数值） |
| C08 | Streak | 打卡火焰 + 天数 | 连续天数（数值） |
| C09 | HeatmapCell | 热力图 7 列格子 | 色阶：empty/l1..l4/today 描边 |
| C10 | TaskCard | 任务面板（复习/新词两行） | — |
| C11 | WordCard | 单词卡片：word+音标+词性+释义+例句 | `模式`: learn（全量）/ review（无释义） |
| C12 | Choice | 四选一选项 | `状态`: idle/correct/wrong |
| C13 | SelfRating | 三态自评按钮组（认识/模糊/不认识） | — |
| C14 | Field | 表单输入框 / 下拉 / 文本域 | — |
| C15 | OptCard | 选项卡（选词书/选词数） | `状态`: normal/sel |
| C16 | Modal | 弹层（纠错） | — |
| C17 | NoteBlock | 黄色线框注释块（交付后删除） | — |
| C18 | SpecTable | 间隔规则表 | — |

## 4. 页面树（Frames 顺序与命名）

| Frame | 页面名 | 主要组件排布 |
|-------|--------|--------------|
| 00 | Landing 落地页 | Hero(C04) → 卖点 3 卡(C05) → 词书 3 卡(C05) → 三步(C05) → Footer |
| 01 | BookDetail 词书详情 | 左主栏：信息卡 + 词条预览表(C18)；右栏：来源许可 + 排序说明 |
| 02 | GuestTrial 游客试学 | 顶部 tag + Progress(C07) + WordCard(learn)(C11) + SelfRating(C13) |
| 03 | Signup 注册 | 表单卡(C14 + 进度合并单选) + C04 |
| 04 | Login 登录 | 表单卡(C14) |
| 05 | Onboarding 首次设置 | 三步骤标签 + OptCard(C15) ×2 组 + C14 |
| 06 | Today 今日首页 | Streak(C08) + TaskCard(C10) + 主按钮(C04) + 侧栏 Heatmap(C09) |
| 07 | NewWord 新词学习 | WordCard(learn)(C11) + SelfRating(C13) + 待巩固列表 |
| 08 | Review 复习 | WordCard(review)(C11) + Choice(C12) ×4 + 等级反馈 |
| 09 | Done 当日完成 | Streak(C08) + 完成数字 + 明日预告 |
| 10 | Backlog 缺席回归 | 积压数字 3 块 + 安正文案 + 双入口(C04) |
| 11 | Stats 进度统计 | 核心数字 3 卡 + Progress(C07) 词书进展 + Heatmap(C09) + SpecTable(C18) |
| 12 | Settings 学习设置 | 左：表单/多选/C14；右：SpecTable(C18) |
| 13 | Books 词书列表 | 3 词书卡(C05 + Progress) + 切换流程注 |
| 14 | Feedback 纠错弹层 | C16 Modal + 位置快照 + C14 |
| 00i | Index 流程总览（不在 Figma 复刻） | 走查导航页，仅 HTML 保留 |

## 5. 页面图层结构与状态标注

每页在 Figma 中建议结构（以 06 今日首页为例）：

```
06_Today/
├── 断点横幅（注释）
├── TopBar（C01）
├── 主区
│   ├── 标题行：H1 + 日期 + Streak(C08)
│   ├── TaskCard(C10)
│   │   ├── 行-复习：文案 + Progress(C07)   [变体: 有/无积压标记]
│   │   ├── 行-新词：文案 + Progress(C07)
│   │   └── 主按钮「先复习」                 [变体: 复习为空时换「学习新词」]
│   └── 边栏：本周打卡(Heatmap) + 今日回顾
└── NoteBlock（注释：状态变体说明）
```

> 关键变体：`06_Today=normal / 06_Today=empty(无任务) / 06_Today=backlog→见10`
> `07_NewWord`、`08_Review` 需有 correct/wrong 反馈态变体。

## 6. 关键状态矩阵（务必每个都有对应变体）

| 页面 | 状态变体 |
|------|---------|
| 02 GuestTrial | 试学前 / 第 5 词后（出现注册引导） |
| 03 Signup | 检测到游客进度（合并单选）/ 无游客进度 |
| 06 Today | normal / empty / 积压(link→10) / 全完成(link→09) |
| 07 NewWord | 自评汇中 / 轮末重现待巩固 / 本轮完成 |
| 08 Review | 作答前（防偷看）/ 答对反馈 / 答错反馈（词回队尾） |
| 10 Backlog | 积压 ≤ 上限（并入今日 / 无分批）/ 积压 > 上限（分批） |
| 12 Settings | 全部词书取消（需提示至少一本） |

## 7. 交互标注（给开发 / 评审用）

> 低保真阶段用「原型 Prototyping」连接即可，交互逻辑最终见 PRD FR 与后端约束。

| 流程 | 起 → 止 |
|------|--------|
| F1 首学漏斗 | 00 → 01 → 02 → 03 → 05 → 06 |
| F2 每日学习 | 06 → 08 → 07 → 09 |
| F3 新词自评 | 07 内循环（不认识→轮末重现） |
| F4 复习决策 | 08 内循环（答错→队尾） |
| F5 缺席回归 | 06(积压) → 10 |
| F6 词书切换 | 13 → 07 / 12 / 11 |

其余「边界/异常」见 PRD FR-01~FR-11，不在原型画板复刻，仅以 NoteBlock（C17）标注。

## 8. 交付时清理清单

- [ ] 删除 C17 NoteBlock（黄色注释块）所在图层
- [ ] 删除 C03 断点横幅
- [ ] 替换示意单词/进度为正式数据（或标记 data=placeholder）
- [ ] 核对与 HTML 页面信息一致（建议以 HTML 走查版为准）