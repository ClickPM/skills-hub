# Excalidraw Backend

Text → Excalidraw scene. Read this after [SKILL.md](../SKILL.md) has picked the backend and diagram type.

---

## Step A — Pick the output mode

| 触发词 | 模式 | 扩展名 | 打开方式 |
|--------|------|--------|---------|
| `Excalidraw`、`画图`、`流程图`、`思维导图`（默认） | **Obsidian** | `.excalidraw.md` | Obsidian Excalidraw 插件直接渲染 |
| `标准Excalidraw`、`standard excalidraw` | **Standard** | `.excalidraw` | excalidraw.com 打开/编辑/分享 |
| `Excalidraw动画`、`动画图`、`animate` | **Animated** | `.animate.excalidraw` | 拖进 excalidraw-animate 生成动画 |

`.excalidraw.md` 是 Obsidian 原生格式：支持反链、搜索索引、frontmatter、"back of the note"。纯 `.excalidraw` 是遗留格式，插件首次保存时会自动转换。**Obsidian 场景一律用 `.excalidraw.md`。**

---

## Step B — Pick the generation path

| 元素数 | 做法 |
|--------|------|
| **< 15** | Claude 直接用 Write 工具写 JSON，照下面的元素规范 |
| **≥ 15** | **必须**走 Python：写一个用 `ExcalidrawBuilder` 的脚本再执行。内联生成 50+ 元素的 JSON 会撞 token 上限且极易出错 |

生成脚本存到 `ai-output/temporary/scripts/`。

---

## Step C — Pick the field profile

两种 profile 的字段集**不同且不可混用**，按目标平台选：

| | **Profile O**（Obsidian） | **Profile W**（excalidraw.com / Animated） |
|---|---|---|
| 产出者 | `ExcalidrawBuilder`（推荐） | 手写 JSON |
| `source` | `https://github.com/zsviczian/obsidian-excalidraw-plugin` | `https://excalidraw.com` |
| `frameId` / `index` / `versionNonce` | **必须有** | **禁止出现** |
| `rawText` / `hasTextLink` | **必须有**（缺 `rawText` 会导致文字重影） | **禁止出现** |
| 文字与形状的关系 | 绑定：text 带 `containerId`，rect 的 `boundElements: [{id,type:"text"}]` + `customData:{"legacyTextWrap":true}` | 独立：`containerId: null`，`boundElements: null`，坐标手算 |
| `updated` | 时间戳（如 `1710100000000`） | `1` |
| `fontFamily` | `3`（等宽，CJK 宽度可预测） | `5`（Excalifont 手写体） |
| `roughness` | `0`（干净，程序化可控） | `1`（手绘感） |
| `lineHeight` | `1.2` | `1.25` |

> `ExcalidrawBuilder.save()` 写 `.excalidraw` 时输出的仍是 Profile O 字段。要做 Standard / Animated 交付，手写 Profile W，别拿 builder 的 `.excalidraw` 顶。

---

## ExcalidrawBuilder API（Profile O）

库位置：`.claude/skills/diagram/scripts/excalidraw_builder.py`

### 脚本骨架

```python
import sys
sys.path.insert(0, ".claude/skills/diagram/scripts")   # 按你的 skill 安装位置调整
from excalidraw_builder import ExcalidrawBuilder

b = ExcalidrawBuilder(seed=42)          # 固定 seed → 可复现

# 标题
b.text("title", 400, 20, 500, 40, "My Diagram Title",
       font_size=24, text_align="center", v_align="top")

# 分组背景（先建，自动置底）
b.group_bg("bg_section1", 50, 80, 400, 200, "#1971c2", bg="#d0ebff")
b.label("section1", 60, 88, "Section 1", font_size=14, stroke_color="#1971c2")

# 带文字的方块
b.box("node1", 70, 120, 170, 60, "Node 1\nSubtitle", "#74c0fc", "#1971c2")
b.box("node2", 260, 120, 170, 60, "Node 2", "#74c0fc", "#1971c2")

# 带标签的箭头
b.arrow("n1_n2", 240, 150, 260, 150, "#1971c2", label_text="connects to")

b.save("Excalidraw/主题/图名.excalidraw.md")
```

执行：`python <脚本路径>`（优先用 vault 根的 `.venv` 解释器）。

### 方法表

| 方法 | 说明 | 生成的 ID |
|------|------|-----------|
| `b.box(prefix, x, y, w, h, text, bg, stroke, **kw)` | 矩形 + 居中绑定文字 | `rect_{prefix}` + `text_{prefix}` |
| `b.label(prefix, x, y, text, **kw)` | 独立文字标签 | `lbl_{prefix}` |
| `b.group_bg(gid, x, y, w, h, stroke, bg=, **kw)` | 虚线分组背景（置底层） | `{gid}` |
| `b.arrow(prefix, x1, y1, x2, y2, color, **kw)` | 箭头 + 可选标签 | `arr_{prefix}` |
| `b.text(tid, x, y, w, h, content, **kw)` | 原始文字元素 | `{tid}` |
| `b.rect(rid, x, y, w, h, bg, stroke, **kw)` | 原始矩形 | `{rid}` |
| `b.save(path)` | 按扩展名自动选格式 | — |

**`box()` 关键参数：** `font_size=16` · `text_align="center"|"left"` · `stroke_color="#1e1e1e"`（深底用 `"#ffffff"`）· `stroke_style="solid"|"dashed"` · `font_family=3`

**`arrow()` 关键参数：** `label_text=None` · `stroke_style` · `bidirectional=False`

**`group_bg()` 关键参数：** `bg=None`（传描边色的浅色调）· `stroke_style="dashed"` · `opacity=30`

### Z-order

Builder 自动分三层，由底到顶：`group_bg()` → `box()`/`label()`/`text()`/`rect()` → `arrow()`。手写 JSON 时同理：背景矩形必须排在数组前面。

---

## Layout guidelines

| 间隔对象 | 最小间距 |
|----------|---------|
| 同组节点（水平） | 20px |
| 同组节点（垂直） | 15px |
| 分组背景内边距 | 四边各 20px |
| 分组之间（水平） | 60px |
| 分组之间（垂直） | 50px |
| 箭头标签相对中点 | Y −15px（压在箭头上方） |

- **画布范围**：元素控制在 0–1200 × 0–800，原点在左上角
- **最小形状尺寸**：带文字的矩形/椭圆不小于 120×60px
- **字号硬下限**：标题 20–28px · 副标题 18–20px · 正文/标签 16–18px · 次要注释 14px · **绝对禁止 < 14px**

### 分组的标准写法

```python
b.group_bg("bg_xxx", X, Y, W, H, stroke_color, bg=light_tint)       # 1. 背景先建
b.label("xxx", X+10, Y+8, "Group Name", font_size=14,
        stroke_color=stroke_color)                                   # 2. 组标题在左上角内侧
b.box("item1", X+20, Y+40, bw, bh, "Content", bg, stroke)            # 3. 内容
b.box("item2", X+20+bw+20, Y+40, bw, bh, "Content 2", bg, stroke)
```

### 独立文字的居中（Profile W 必用）

Excalidraw 的独立 text 元素 `x` 是**左边缘**，没有自动居中：

```
estimatedWidth = len(text) * fontSize * 0.5      # CJK 字符系数用 1.0
x = centerX - estimatedWidth / 2
```

例：`"Hello"`（5 字符，fontSize 20）居中于 x=300 → `5*20*0.5 = 50` → `x = 275`。

---

## Element specification

### Profile O — 矩形（Obsidian）

```json
{
  "id": "unique_id", "type": "rectangle",
  "x": 0, "y": 0, "width": 300, "height": 120,
  "angle": 0, "strokeColor": "#STROKE", "backgroundColor": "#BG",
  "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
  "roughness": 0, "opacity": 100,
  "groupIds": [], "frameId": null,
  "roundness": {"type": 3},
  "seed": 100001, "version": 2, "versionNonce": 100002,
  "isDeleted": false,
  "boundElements": [{"id": "text_id", "type": "text"}],
  "customData": {"legacyTextWrap": true},
  "updated": 1710100000000, "link": null, "locked": false,
  "index": "a0", "hasTextLink": false
}
```

### Profile O — 绑定文字

```json
{
  "id": "text_id", "type": "text",
  "x": 10, "y": 10, "width": 280, "height": 100,
  "angle": 0, "strokeColor": "#1e1e1e", "backgroundColor": "transparent",
  "fillStyle": "solid", "strokeWidth": 1, "strokeStyle": "solid",
  "roughness": 0, "opacity": 100,
  "groupIds": [], "frameId": null, "roundness": null,
  "seed": 200001, "version": 2, "versionNonce": 200002,
  "isDeleted": false, "boundElements": null,
  "updated": 1710100000000, "link": null, "locked": false,
  "text": "Label\nSubtext", "fontSize": 16, "fontFamily": 3,
  "textAlign": "center", "verticalAlign": "middle",
  "containerId": "parent_rect_id",
  "originalText": "Label\nSubtext",
  "autoResize": true, "lineHeight": 1.2,
  "index": "a1", "hasTextLink": false, "rawText": "Label\nSubtext"
}
```

### Profile O — 箭头

```json
{
  "id": "arrow_id", "type": "arrow",
  "x": 100, "y": 200, "width": 200, "height": 100,
  "angle": 0, "strokeColor": "#COLOR", "backgroundColor": "transparent",
  "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
  "roughness": 0, "opacity": 100,
  "groupIds": [], "frameId": null,
  "roundness": {"type": 2},
  "seed": 300001, "version": 2, "versionNonce": 300002,
  "isDeleted": false, "boundElements": null,
  "updated": 1710100000000, "link": null, "locked": false,
  "points": [[0, 0], [200, 100]],
  "lastCommittedPoint": null,
  "startBinding": null, "endBinding": null,
  "startArrowhead": null, "endArrowhead": "arrow",
  "index": "a2", "hasTextLink": false
}
```

`width`/`height` 取 `abs(dx)`/`abs(dy)`，而 `points` 用带符号的 `[dx, dy]`。

### Profile W — 通用元素（excalidraw.com / Animated）

不要加 `frameId`、`index`、`versionNonce`、`rawText`；`boundElements` 用 `null` 而非 `[]`；`updated` 用 `1`。

```json
{
  "id": "unique-id",
  "type": "rectangle|text|arrow|ellipse|diamond",
  "x": 100, "y": 100, "width": 200, "height": 50,
  "angle": 0,
  "strokeColor": "#1e1e1e",
  "backgroundColor": "transparent",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "strokeStyle": "solid|dashed|dotted",
  "roughness": 1,
  "opacity": 100,
  "groupIds": [],
  "roundness": {"type": 3},
  "seed": 123456789,
  "version": 1,
  "isDeleted": false,
  "boundElements": null,
  "updated": 1,
  "link": null,
  "locked": false
}
```

文字元素追加：

```json
{
  "text": "显示文本",
  "fontSize": 20,
  "fontFamily": 5,
  "textAlign": "center",
  "verticalAlign": "middle",
  "containerId": null,
  "originalText": "显示文本",
  "autoResize": true,
  "lineHeight": 1.25
}
```

`strokeStyle` 三值：`solid`（默认）/ `dashed`（可选路径、异步流、弱关联）/ `dotted`。

完整元素类型清单见 [excalidraw-schema.md](excalidraw-schema.md)。

---

## Scene wrapper

**Profile O（`.excalidraw.md`）** —— `ExcalidrawBuilder._save_md()` 已处理好，手写时严格照抄这个结构：

````markdown
---

excalidraw-plugin: parsed
tags: [excalidraw]

---
==⚠  Switch to EXCALIDRAW VIEW in the MORE OPTIONS menu of this document. ⚠==


# Excalidraw Data

%%
## Text Elements

## Drawing
```json
{完整 scene JSON}
```
%%
````

- `## Text Elements` **必须留在 `%%` 注释块内部且留空**——插件首次保存时自行填充 `text ^elementId`；放到 `%%` 外面，Obsidian 会把 `^id` 块引用当正文渲染成重影文字
- frontmatter 只放 `excalidraw-plugin: parsed` 和 `tags: [excalidraw]`

scene JSON 顶层：

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "https://github.com/zsviczian/obsidian-excalidraw-plugin",
  "elements": [...],
  "appState": {"theme": "light", "viewBackgroundColor": "#ffffff", "gridSize": null},
  "files": {}
}
```

**Profile W（`.excalidraw`）** —— 纯 JSON，无 Markdown 包装：

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "https://excalidraw.com",
  "elements": [...],
  "appState": {"gridSize": null, "viewBackgroundColor": "#ffffff"},
  "files": {}
}
```

---

## Animated mode

Profile W 之上，每个元素加 `customData.animate`：

```json
{
  "id": "title-1",
  "type": "text",
  "customData": {
    "animate": {"order": 1, "duration": 500}
  }
}
```

- `order` 越小越先出现；相同 `order` 同时出现
- `duration` 为该元素绘制时长（毫秒），默认 500
- 建议顺序：标题 → 主要框架 → 连接线 → 细节文字

用法：生成 `.animate.excalidraw` → 拖进 <https://dai-shi.github.io/excalidraw-animate/> → Animate 预览 → 导出 SVG 或 WebM。

---

## Lessons learned（生产踩坑）

1. **复杂图必须用 Python 脚本。** 内联 JSON 有 token 上限，50+ 元素几乎必错。
2. **Profile O 的文字元素必须带 `rawText` 和 `hasTextLink`。** 缺 `rawText` 会在插件处理 `.excalidraw.md` 时渲染出重影文字；容器矩形要带 `customData: {"legacyTextWrap": true}`。
3. **`roughness=0` 用于干净的专业图。** 默认手绘感（`roughness=1`）程序化控制困难，只在 Profile W 保留。
4. **`fontFamily=3`（等宽）** 让 CJK 字符宽度计算稳定。
5. **背景分组必须先于内容创建**（手写 JSON 时体现为数组顺序在前）。
6. **`seed` 与 `versionNonce` 必须唯一**，用固定 seed 的 `random.randint()` 保证可复现。
7. **元素需要 `index` 字段**才能在 `.excalidraw.md` 里正确分层，`build_scene()` 自动分配。

---

## Common mistakes

- **文字偏移** —— 独立 text 的 `x` 是左边缘不是中心，必须手算居中公式
- **元素重叠** —— y 坐标相近的元素易堆叠，放置前检查 ≥20px 间距
- **画布留白不足** —— 四周留 50–80px padding，别贴边
- **标题没有居中于图表整体宽度** —— 不是固定在 x=0
- **箭头标签溢出** —— 长标签（如 "ATP + NADPH"）会超出短箭头，保持标签短或加长箭头
- **对比度不够** —— 白底文字不浅于 `#757575`，有色文字用深色变体
- **字号太小** —— 正文最小 16px，绝对下限 14px

---

## Excalidraw checklist

- [ ] 输出模式与目标平台匹配（Obsidian / Standard / Animated）
- [ ] Profile 字段集正确且未混用（见 Step C 对照表）
- [ ] 所有 `id` 全局唯一；`seed`/`versionNonce` 唯一
- [ ] Profile O：text 的 `containerId` 与父矩形 `id` 对应，矩形 `boundElements` 含该 text `id`
- [ ] Profile O：text 有 `rawText`；容器矩形有 `customData: {"legacyTextWrap": true}`
- [ ] Profile W：无 `frameId`/`index`/`versionNonce`/`rawText`，`boundElements: null`，`updated: 1`
- [ ] 箭头 `points[1]` 为带符号位移，`width`/`height` 为其绝对值
- [ ] 背景分组排在内容之前
- [ ] 深色底用白字，浅色底用深色变体
- [ ] 元素无重叠，字号不低于 14px
- [ ] `.excalidraw.md` 的 `## Text Elements` 在 `%%` 内且为空
- [ ] 保存到 `Excalidraw/<主题>/`，未平铺到根目录

---

## Example report to the user

**Obsidian 模式**

```
Excalidraw 图已生成：Excalidraw/公布运价/订单流程.excalidraw.md

在 Obsidian 中打开该文件，插件会直接渲染；
若显示为 Markdown，点右上角 MORE OPTIONS → Switch to EXCALIDRAW VIEW。
```

**Standard 模式**

```
Excalidraw 图已生成：Excalidraw/公布运价/订单流程.excalidraw

打开 https://excalidraw.com → 左上角菜单 Open → 选择该文件（或直接拖进页面）。
```

**Animated 模式**

```
Excalidraw 动画图已生成：Excalidraw/公布运价/订单流程.animate.excalidraw

动画顺序：标题(1) → 主框架(2-4) → 连接线(5-7) → 说明文字(8-10)

打开 https://dai-shi.github.io/excalidraw-animate/ → Load File → 预览 → Export SVG/WebM。
```
