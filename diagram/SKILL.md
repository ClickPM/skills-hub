---
name: diagram
description: Generate a diagram from text, routing to Mermaid, Excalidraw, or Obsidian Canvas. Covers flowcharts, mindmaps, architecture and OKR trees, sequence and state diagrams, comparisons, timelines, and turning a PRD's written business flow into a diagram. Triggers on 画图, 流程图, 思维导图, 架构图, 对比图, 可视化, PRD流程图, 核心流程画图, diagram, flowchart, mindmap, Mermaid, Excalidraw, 动画图, animate, Canvas, .canvas.
metadata:
  version: 2.1.0
  replaces: mermaid-visualizer, excalidraw-diagram, excalidraw-scene-from-graph, obsidian-canvas-creator, prd-flow-graph-from-text
---

# Diagram

One skill, three rendering backends. Decide the backend first, then the diagram type, then read the matching reference and generate.

> **入口特例 —— PRD 里的流程文字。** 输入是 PRD 用自然语言写的业务流程（「用户从航班列表进入舱位页…」），先读 [references/prd-flow.md](references/prd-flow.md)：它给出「流程文字 → 图结构 → 渲染」的抽取规则和 PRD 落地约定，再回到下面的后端选择完成渲染。其余情况直接从 Step 1 开始。

---

## Step 1 — Pick the backend

| Backend | Output | Use when |
|---------|--------|----------|
| **Mermaid** | ```` ```mermaid ```` fence, inline in a `.md` file | The diagram lives **inside** a document (PRD, 周报, wiki 概念页, README). Renders in Obsidian and GitHub, diffs as text, costs almost nothing. |
| **Excalidraw** | `.excalidraw.md` (Obsidian) / `.excalidraw` (excalidraw.com) | Standalone visual deliverable — 架构图, OKR 树, 培训页, 汇报配图. Precise coordinates, hand-drawn style, exportable to SVG/PNG, animatable. |
| **Canvas** | `.canvas` (JSON Canvas) | An **interactive workspace** in Obsidian: nodes the user drags around, nodes that embed real vault notes (`file` nodes), 无限画布 brainstorming. |

**Routing rules, in order:**

1. User named a format (`Mermaid` / `Excalidraw` / `标准Excalidraw` / `动画图` / `Canvas` / `.canvas`) → obey it.
2. Output is to be **embedded into an existing document** → Mermaid.
3. Diagram must **link to or embed vault notes**, or the user wants to keep rearranging it by hand → Canvas.
4. Standalone diagram file, or needs styling control beyond what Mermaid offers → Excalidraw.
5. Still ambiguous → **Mermaid** (cheapest, most portable), and offer to regenerate as Excalidraw or Canvas.

Then read exactly one reference:

- [references/mermaid.md](references/mermaid.md)
- [references/excalidraw.md](references/excalidraw.md)
- [references/canvas.md](references/canvas.md)

---

## Step 2 — Pick the diagram type

Applies to every backend. Match content structure, don't default to "flowchart" reflexively.

| 类型 | English | 使用场景 | 做法 |
|------|---------|---------|------|
| **流程图** | Flowchart | 步骤说明、工作流程、任务执行顺序 | 箭头连接各步骤，清晰表达流程走向 |
| **思维导图** | Mind Map | 概念发散、主题分类、灵感捕捉 | 中心向外发散，放射状结构 |
| **层级图** | Hierarchy | 组织结构、内容分级、系统拆解、OKR 树 | 自上而下或自左至右构建层级节点 |
| **关系图** | Relationship | 要素之间的影响、依赖、互动 | 图形间连线表示关联，箭头 + 说明 |
| **对比图** | Comparison | 两种以上方案或观点的对照分析 | 左右两栏或表格形式，标明比较维度 |
| **时间线图** | Timeline | 事件发展、项目进度、模型演化 | 以时间为轴，标出关键时间点与事件 |
| **矩阵图** | Matrix | 双维度分类、任务优先级、定位 | 建立 X / Y 两个维度，坐标平面安置 |
| **序列图** | Sequence | 组件间交互、API 调用、消息流 | 时间轴布局，actor 分列，激活框 |
| **状态图** | State | 系统状态、状态流转、生命周期 | 状态节点 + 带标签的转移边 |
| **自由布局** | Freeform | 内容零散、灵感记录、初步信息收集 | 无结构限制，自由放置图块与箭头 |

Backend coverage: Mermaid does 流程图/思维导图/层级图/关系图/对比图/序列图/状态图 natively; 时间线/矩阵/自由布局 are better in Excalidraw or Canvas.

---

## Step 3 — Universal design rules

These hold for all three backends. Backend-specific mechanics are in the references.

### Text

- **禁止 Emoji** — 图表文本中不使用任何 Emoji。需要视觉标记就用形状（圆/方/箭头）或颜色区分。
- **引号替换** — 文本中的 `"` 写成 `『』`，`()` 写成 `「」`。三种格式的解析器都会被裸引号/括号绊倒。
- **节点文字简短** — 每个节点 ≤ 2 行；长内容拆成子节点，或（Canvas）改用 `file` 节点指向笔记。
- **首次出现的英文术语加中文注释**（如「检索增强生成 (RAG)」），与 vault 文档规范一致。

### Layout

- **间距** — 元素之间留足空隙，宁可稀疏不要重叠；具体数值见各 backend 参考。
- **留白** — 内容不贴边，画布四周留 50-80px padding。
- **标题居中于图表整体宽度**，不是固定在 x=0。
- **层次清晰** — 用颜色和形状区分信息层级，不要一片同色。

### Semantic color palette

统一语义色板（Open Color 体系），三种 backend 共用同一套语义，只是写法不同：

| 语义 | 浅填充 | 深描边/文字 |
|------|--------|------------|
| 输入 / 数据源 / 前端 / 用户侧 | `#a5d8ff` | `#1971c2` |
| 成功 / 输出 / 已完成 / 后端基础设施 | `#b2f2bb` | `#2f9e44` |
| 警告 / 待处理 / 外部依赖 / AI 工具 | `#ffd8a8` | `#e8590c` |
| 处理中 / 中间件 / 服务集成 | `#d0bfff` | `#7048e8` |
| 错误 / 关键 / 告警 / 执行器 | `#ffc9c9` | `#c92a2a` |
| 备注 / 决策 / 规划 | `#fff3bf` | `#e67700` |
| 存储 / 数据 / 缓存 / 知识库 | `#c3fae8` | `#0ca678` |
| 分析 / 指标 / 统计 | `#eebefa` | `#862e9c` |
| 中性 / 传统系统 / 工具 | `#e9ecef` | `#495057` |

分层区域背景（大矩形，opacity 30）：`#dbe4ff` 前端/UI 层 · `#e5dbff` 逻辑/处理层 · `#d3f9d8` 数据/工具层。

**对比度硬规则：** 白底文字不浅于 `#757575`；浅色填充上用同色系深色变体（浅绿底配 `#2f9e44`，不配 `#69db7c`）；深色填充上用白字。

---

## Step 4 — Save to the right place

| Backend | 保存位置 |
|---------|---------|
| Mermaid | 直接写进目标文档；独立留存时放 `ai-output/temporary/drafts/` |
| Excalidraw | `Excalidraw/<主题>/<名称>.excalidraw.md` — **禁止平铺到 `Excalidraw/` 根目录**，按业务主题建子目录（`Excalidraw/公布运价/`、`Excalidraw/周报/`、`Excalidraw/支付/`），不存在则先建 |
| Canvas | `canvas/<名称>.canvas` |
| 生成脚本（Excalidraw 复杂图） | `ai-output/temporary/scripts/` |

文件名优先中文，便于检索。

---

## Step 5 — Report back

生成后告诉用户：

1. 文件路径（可点击）
2. 打开方式（Obsidian / excalidraw.com / excalidraw-animate，见各 backend 参考）
3. **设计选择说明** —— 选了哪种 backend 和图表类型、为什么
4. 是否需要调整

---

## Shared quality checklist

- [ ] Backend 选择与用途匹配（嵌文档→Mermaid，独立图→Excalidraw，可交互→Canvas）
- [ ] 图表类型与内容结构匹配
- [ ] 无 Emoji
- [ ] 引号/括号已替换为 `『』` / `「」`
- [ ] 颜色语义一致，对比度达标
- [ ] 元素无重叠，画布有留白
- [ ] 保存路径符合上表约定
- [ ] Backend 专属检查项（见对应参考文档末尾的 checklist）

---

## Files

```
.claude/skills/diagram/
├── SKILL.md                              # 本文件：backend 路由 + 共享规范
├── references/
│   ├── prd-flow.md                       # 入口：PRD 流程文字 → 图结构 → 渲染
│   ├── mermaid.md                        # Mermaid 图表类型、配置、关键语法
│   ├── mermaid-syntax.md                 # Mermaid 完整语法参考与排错
│   ├── excalidraw.md                     # 三种输出模式、Builder API、元素规范
│   ├── excalidraw-schema.md              # Excalidraw 元素 JSON schema
│   ├── canvas.md                         # Canvas 工作流、节点尺寸、配色
│   ├── canvas-spec.md                    # JSON Canvas 1.0 规范
│   └── canvas-layout-algorithms.md       # MindMap / Freeform 布局算法
└── scripts/
    ├── excalidraw_builder.py             # ExcalidrawBuilder 库（复杂图必用）
    └── example_architecture.py           # 示例：三分组架构图
```

上游来源：Mermaid / Excalidraw / Canvas 三套规则原属 [axtonliu/axton-obsidian-visual-skills](https://github.com/axtonliu/axton-obsidian-visual-skills)，Python builder 为本仓库自建。
