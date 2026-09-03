# Obsidian Canvas Backend

Text → `.canvas` (JSON Canvas). Read this after [SKILL.md](../SKILL.md) has picked the backend and diagram type.

Canvas 的独有价值在于**可交互**：节点可以拖动重排，`file` 节点能直接嵌入 vault 里的真实笔记，画布无限延展。只要图是「给人继续摆弄的工作台」而非「定稿的插图」，就选 Canvas。

---

## Step A — Pick the layout type

| 布局 | 结构 | 适用 |
|------|------|------|
| **MindMap** | 中心向外放射，父子层级清晰 | 头脑风暴、主题拆解、层级内容 |
| **Freeform** | 自由定位，多种连接类型 | 复杂网络、非层级内容、自定义分区 |

从上下文推断；实在看不出就问用户一次。

---

## Step B — Plan the structure

**MindMap**：确定中心概念（根节点）→ 一级分支（主题）→ 二级分支（子主题）→ 叶子节点（细节）。

**Freeform**：先聚类相关概念 → 识别连接模式 → 规划空间分区 → 考虑视觉动线。

---

## Step C — Generate the JSON

顶层只有 `nodes` 和 `edges` 两个数组，不套额外对象、不写注释。完整字段定义见 [canvas-spec.md](canvas-spec.md)。

### 节点

- **ID**：8–12 位随机十六进制字符串，全局唯一（节点与边共用命名空间）
- **尺寸**：按文本长度取（见下表）
- **坐标**：不重叠，间距达标
- **类型**：`text`（内联文本）/ `file`（嵌入 vault 笔记）/ `link`（外链）/ `group`（容器）

> 内容超过两行就别硬塞 `text` 节点——改用 `file` 节点指向真实笔记，这正是 Canvas 优于 Excalidraw 的地方。

### 边

- 连接父子关系
- 层级用直线，跨区交叉引用用曲线
- 复杂关系加 `label`
- 每条边必须引用存在的节点 ID

### 分组（可选）

- 为相关节点创建可视容器
- 背景色克制
- **必须**加描述性 `label`，否则 Obsidian 侧边栏导航会缺项

---

## Step D — Apply the layout algorithm

详细算法见 [canvas-layout-algorithms.md](canvas-layout-algorithms.md)。核心原则：

**MindMap**
- 根节点置于 `(0, 0)`
- 一级节点按角度均匀放射分布
- 二级节点按同级兄弟数量分配扇区
- 最小间距：水平 320px、垂直 200px（按**中心点**计算）

**Freeform**
- 先做逻辑分组
- 分组之间留出明显间隔
- 跨组连接走曲线
- 平衡画布各象限的视觉重量

---

## Node sizing

| 文本长度 | 尺寸 |
|----------|------|
| < 30 字符 | 220 × 100 |
| 30–60 字符 | 260 × 120 |
| 60–100 字符 | 320 × 140 |
| > 100 字符 | 320 × 180（此时应考虑改用 `file` 节点） |

---

## Colors

Canvas 支持预设色号和 hex 两种写法。优先用预设色号（跟随主题、深浅色模式都可读）：

| 预设 | 颜色 | 对应 SKILL.md 语义 |
|------|------|-------------------|
| `"1"` | 红 | 错误 / 关键 / 告警 |
| `"2"` | 橙 | 警告 / 待处理 / 外部依赖 |
| `"3"` | 黄 | 备注 / 决策 / 规划 |
| `"4"` | 绿 | 成功 / 输出 / 已完成 |
| `"5"` | 青 | 存储 / 数据 / 信息细节 |
| `"6"` | 紫 | 概念 / 抽象 / 处理中 |

语义色板里没有预设色号的（蓝 / 粉 / 灰），写大写 hex：`"#A5D8FF"` / `"#EEBEFA"` / `"#E9ECEF"`。

颜色用来编码含义，不做装饰。

---

## Critical rules

1. **引号转义** —— 中文双引号 → `『』`，中文单引号 → `「」`，英文双引号 → `\"`。转义不一致会直接破坏 JSON 解析。
2. **ID 唯一** —— 8–12 位随机 hex，节点和边都不能重复。
3. **Z-index 顺序** —— 数组里先输出 `group`（底层），再输出子分组，最后输出 `text`/`file`/`link` 节点（顶层）。
4. **间距** —— 中心点水平 ≥320px、垂直 ≥200px，计算时算上节点自身尺寸。
5. **JSON 结构** —— 顶层仅 `nodes` / `edges`，无包装对象、无注释。
6. **输出即文件** —— 直接写 `.canvas`，不要在回答里贴整段 JSON。

---

## Validate before saving

- 所有节点 ID 唯一
- 无坐标重叠（中心距 > 节点尺寸 + 间距）
- 所有边引用的节点 ID 都存在
- 所有 `group` 都有 `label`
- 颜色格式统一（预设色号或大写 hex）
- 引号已按规则转义
- 无孤立节点（除非是有意为之的独立岛）

保存到 `canvas/<名称>.canvas`。

---

## Examples

**简单 MindMap**

> "Create a mind map about solar system planets"

1. 中心：Solar System
2. 一级分支：Inner Planets / Outer Planets / Dwarf Planets
3. 二级节点：各行星 + 关键事实
4. 应用放射布局
5. 生成 JSON，间距达标

**文章转 Canvas**

> "Turn this article into a canvas" + 文章正文

1. 抽取文章结构（引言、正文各节、结论）
2. 识别关键概念与关系
3. 相关章节在空间上聚类
4. 用带标签的边连接
5. Freeform 布局，分区清晰

---

## Tips

1. **文本简洁** —— 每个节点可扫读（≤2 行）
2. **用层级** —— 按重要性和关系分组
3. **平衡画布** —— 分散节点，避免聚成一团
4. **战略性用色** —— 颜色编码含义
5. **有意义的连接** —— 只画能澄清关系的边
6. **在 Obsidian 里实测** —— 确认文件能正常打开

---

## Common pitfalls

- 节点重叠（务必检查距离）
- 引号转义不一致（破坏 JSON 解析）
- 分组缺 `label`（侧边栏导航异常）
- 节点塞太多文字（该用 `file` 节点）
- ID 重复
- 孤立节点（除非有意）

---

## Reference documents

- [canvas-spec.md](canvas-spec.md) —— JSON Canvas 1.0 完整规范，处理边界情况时读
- [canvas-layout-algorithms.md](canvas-layout-algorithms.md) —— MindMap / Freeform 详细定位算法与碰撞检测，做复杂布局计算时读
