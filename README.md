# 英语学习网站 MVP

面向四六级 / 考研学生的 **Web 端背单词产品**：浏览器即用、词频降序高频先背、间隔规则全透明、缺席回归分批容错不施压。

本仓库是一个从 **PRD → 低保真原型 → 可运行 MVP** 的完整产品交付，附带全套单元测试。

![定位](https://img.shields.io/badge/定位-Web%20背单词产品-blue)
![测试](https://img.shields.io/badge/测试-27%20passed-brightgreen)

## 目录

- [核心差异化](#核心差异化)
- [项目交付物](#项目交付物)
- [技术栈](#技术栈)
- [快速开始](#快速开始)
- [运行测试](#运行测试)
- [项目结构](#项目结构)
- [核心产品机制](#核心产品机制)
- [里程碑与后续规划](#里程碑与后续规划)

## 核心差异化

| 维度 | 本产品 | 市面常见做法 |
|------|--------|--------------|
| 载体 | Web 响应式，浏览器即用、零安装 | 需下载 App |
| 词序 | 按词频降序，高频先背、获得感前置 | 多按字母序排列 |
| 算法 | 间隔规则全公开（1/3/7/14/30 天），用户可感知 | 复习算法黑盒 |
| 容错 | 缺席回归积压分批摊开，无惩罚、可追平 | 缺席即积压崩溃，用户直接放弃 |
| 数据 | 登录后进度云同步（后续支持导出） | 换设备即丢失 |

**北极星指标：7 日留存率。**

## 项目交付物

| 交付物 | 位置 | 说明 |
|--------|------|------|
| 产品需求文档（PRD） | [`docs/PRD_source.md`](docs/PRD_source.md) | 723 行完整 PRD：背景痛点、用户画像、旅程地图、11 条 FR、用户故事、埋点指标、里程碑、风险 |
| AI 学习助手 PRD（AI 版） | [`docs/PRD_AI学习助手.md`](docs/PRD_AI学习助手.md) | AI 功能迭代 PRD：LLM 输入输出定义、RAG、Prompt 架构、评测体系（准确率/幻觉率/采纳率）、成本预算、灰度计划 |
| PRD Word 版 | `docs/PRD_英语学习网站MVP.docx` | 便于评审传阅 |
| 低保真原型（15 页） | [`docs/Prototype/html/index.html`](docs/Prototype/html/index.html) | 灰阶线框 + 6 条核心流程走查，含移动端断点标注 |
| PRD × 原型映射表 | [`docs/Prototype/PRD_prototype_mapping.md`](docs/Prototype/PRD_prototype_mapping.md) | 双向对照单一事实源，由脚本强制校验 |
| Figma 搭建规格 | `docs/Prototype/figma/figma_spec.md` | 页面树 / 组件 / 栅格 / token |
| 可运行 MVP | `app/` | FastAPI 全栈实现，游客试学到打卡全链路 |
| 测试套件 | `tests/` | 27 个测试，覆盖核心算法与 API |

## 技术栈

- **后端**：FastAPI + SQLAlchemy 2.0 + Pydantic v2
- **数据库**：MySQL（默认）/ SQLite（测试与本地体验）
- **前端**：Jinja2 模板 + 原生 CSS（响应式，360–1440px）
- **认证**：JWT + HttpOnly Cookie + bcrypt
- **数据**：ECDICT 开源词库（词频降序切分词书）
- **测试**：pytest + httpx TestClient

## 快速开始

```bash
# 1. 克隆并进入虚拟环境
git clone <repo-url>
cd 英语学习
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量（创建 .env）
#    本地体验可用 SQLite：
DATABASE_URL=sqlite:///./english_mvp.db
#    或使用 MySQL：
# DATABASE_URL=mysql+pymysql://user:password@localhost:3306/english_mvp?charset=utf8mb4
# SECRET_KEY=换成你自己的随机串

# 4. 初始化数据库并导入词书
python -m app.init_db
python -m app.seed.import_ecdict   # 需要 data/ecdict.csv（见下方说明）

# 5. 启动
python run.py
# 打开 http://127.0.0.1:8000 ，游客先试学 5 个词即可体验全链路
```

> 词表说明：`data/ecdict.csv` 为 ECDICT 开源词库（体积较大，不入库）。
> 从 [skywind3000/ECDICT](https://github.com/skywind3000/ECDICT) 下载后放入 `data/` 目录。
> 开源协议要求署名，网站页脚已包含数据来源声明。

## 运行测试

```bash
pytest
```

测试默认使用独立的 SQLite 数据库（`data_test.db`，已加入 `.gitignore`），不会影响本地数据。

当前状态：**27 passed**。测试重点覆盖：

- `test_scheduler.py`：间隔调度确定性序列（FR-06 验收：给定作答序列，间隔可复现）
- `test_backlog.py`：缺席积压分批（FR-07 验收：超上限即拆批，不惩罚）
- `test_streak.py`：连续打卡边界（今日未打卡、断卡、空集）
- `test_api.py` / `test_services.py`：注册登录、游客试学、学习复习全链路

## 项目结构

```
.
├── app/
│   ├── main.py           # FastAPI 入口，挂载路由与静态资源
│   ├── models.py         # 数据模型（用户 / 词书 / 记忆状态 / 答题日志 / 埋点事件）
│   ├── auth.py           # 密码哈希、JWT 签发与鉴权
│   ├── config.py         # 配置（读取 .env）
│   ├── routers/          # 页面 + API 路由
│   │   ├── pages.py      # 落地 / 试学 / 今日 / 学习 / 复习 / 统计 等页面
│   │   ├── auth.py       # 注册 / 登录 / 登出 / onboarding（含游客进度合并）
│   │   ├── learn.py      # 新词学习队列与自评提交
│   │   ├── review.py     # 复习四选一队列与作答提交
│   │   └── misc.py       # 反馈、事件等
│   ├── services/         # 核心业务（纯函数优先，可单测）
│   │   ├── scheduler.py  # 间隔调度引擎（L1-L5，FR-06）
│   │   ├── backlog.py    # 缺席分批容错（FR-07）
│   │   ├── streak.py     # 连续打卡计算（FR-08）
│   │   ├── queue.py      # 今日任务面板 / 复习队列组装（FR-03）
│   │   ├── words.py      # 词卡序列化与四选一干扰项生成（FR-05）
│   │   ├── checkin.py    # 打卡判定
│   │   └── stats.py      # 进度统计（FR-09）
│   ├── seed/             # ECDICT 导入与内容抽检
│   ├── templates/        # Jinja2 页面模板
│   └── static/style.css  # 全局样式
├── docs/
│   ├── PRD_source.md     # 产品需求文档
│   ├── Prototype/        # 低保真原型 + 映射表 + Figma 规格
│   └── tools/            # PRD / 原型校验脚本、流程图生成、线框截图
├── tests/                # pytest 测试套件
├── AGENTS.md             # 开发规范：每次改动必须 commit + 测试通过
└── run.py                # 本地启动
```

## 核心产品机制

### 1. 间隔调度（透明可解释）

| 记忆等级 | L1 | L2 | L3 | L4 | L5 |
|----------|----|----|----|----|-----|
| 间隔（天） | 1 | 3 | 7 | 14 | 30（循环） |

- 新词自评：**认识 → L2（3 天）**；**模糊 → L1（1 天）**；**不认识 → 本轮末尾重现，当场记牢**
- 复习四选一：**答对升级**（封顶 L5）；**答错回落 L1** 并回今日队尾直到答对
- 间隔从本次复习日起算，规则公开在设置页——把"为什么复习这个词"的知情权还给用户

### 2. 缺席分批容错（流失率最高的时刻，也是产品最用心的地方）

```
每日复习上限 = 每日新词数 × 3
积压 ≤ 上限 → 全部并入今日
积压 > 上限 → 今日消化第一批，其余顺延，每日自动追平
```

全程无惩罚性文案，用「追得回来」替代「算了不背了」。

### 3. 首学漏斗（注册门槛必须放在第一次正反馈之后）

```
落地页 → 词书详情 → 游客试学 5 词 → 注册（进度无缝合并）→ 首次设置 → 今日首页
```

任何注册要求都发生在用户「第一次记住一个词」之后——这是首学漏斗完成率 ≥ 60% 的核心设计。

## 里程碑与后续规划

| 里程碑 | 交付内容 | 验收标准 | 状态 |
|--------|---------|---------|------|
| M1 内容入库 | 3 本词书、词频排序、抽检 | 高频 500 词准确率 ≥ 99% | ✅ |
| M2 学习闭环 | 游客 → 注册 → 选词书 → 首学 5 词 | 首学漏斗 ≥ 60% | ✅ |
| M3 复习与容错 | 复习队列 + 四选一 + 分批容错 + 打卡 | 缺席 7 天回归任务量受控 | ✅ |
| M4 上线内测 | 部署、埋点、反馈入口 | 可观测 7 日留存，输出 V2 决策 | ⏳ |

**V2+ 方向**（详见 PRD §12）：阅读联动点词入生词本、CSV/Anki 数据导出、口语 ASR 练习、轻激励体系；**AI 方向**（详见 [`docs/PRD_AI学习助手.md`](docs/PRD_AI学习助手.md)）：词条记忆技巧、复习错因解析、AI 学习周报。

## 文档导航

- 想了解**为什么做这个产品** → [`docs/PRD_source.md`](docs/PRD_source.md) §1 背景与问题陈述
- 想了解**具体功能怎么定义** → PRD §5 功能需求详细说明（FR-01 ~ FR-11）
- 想快速走查**交互流程** → 打开 `docs/Prototype/html/index.html`
- 想了解**开发规范** → [`AGENTS.md`](AGENTS.md)