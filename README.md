# skills-hub

自用的 Claude Code / Codex skills。每个顶层目录是一个 skill,目录名 = `SKILL.md` frontmatter 里的 `name`。

## 安装

```bash
npx skills add ClickPM/skills-hub --skill <name>
```

或者把某个目录整个拷进 `.claude/skills/`(Claude Code)/ `.agents/skills/`(Codex)。

## 目录

| skill | 做什么 | 出处 |
|---|---|---|
| `defuddle` | 用 Defuddle CLI 把网页正文抽成干净 markdown,省 token,替代 WebFetch | 改自 kepano/obsidian-skills(MIT) |
| `obsidian-markdown` | 写 Obsidian 风味 markdown(wikilink、嵌入、callout、properties) | 改自 kepano/obsidian-skills(MIT) |
| `obsidian-cli` | 用官方 `obsidian` CLI 驱动正在运行的桌面端做库级查询;另附完整命令参考 | 改自 kepano/obsidian-skills(MIT),扩写较多 |
| `diagram` | 从文本生成图:按需路由到 Mermaid / Excalidraw / Obsidian Canvas | 三套规则原属 axtonliu/axton-obsidian-visual-skills,Python builder 自建 |
| `ppt-master` | 生成 PPT:SVG 排版 → 导出,含配图生成 / 检索与图表流程 | 自建;**不含 `templates/`**(图标库为第三方、版式含机构品牌资产),自行按 `workflows/create-template.md` 补 |
| `wiki-init` | 在当前工作区初始化 OKF(Open Knowledge Format)知识包 | 自建 |
| `wiki-compile` | 把原始文档编译成结构化 OKF 知识包(扫描变更 → 抽概念 → 写索引) | 自建 |
| `wiki-lint` | 体检已编译的 OKF 包:一致性、新鲜度、覆盖度、缺口分析 | 自建 |
| `wiki-query` | 拿已编译的 OKF 包当结构化上下文回答问题 | 自建 |

## 上游

`defuddle` / `obsidian-markdown` / `obsidian-cli` 改自 Obsidian 官方的
[kepano/obsidian-skills](https://github.com/kepano/obsidian-skills)(MIT),各自目录内带上游 `LICENSE`。
未改动的 `obsidian-bases` 与 `json-canvas` 请直接用上游那份。

也在 https://www.kzgai.cloud/skills 上可读可下载。
