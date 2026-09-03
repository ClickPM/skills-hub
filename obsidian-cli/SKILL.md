---
name: obsidian-cli
description: >
  Drive the running Obsidian desktop app from the terminal via the official
  `obsidian` CLI. Use for vault-level semantic queries that Read/Grep cannot
  answer — backlinks, orphans, unresolved links, tag counts, vault-wide task
  lists, frontmatter property aggregation, outlines, word counts, Base queries,
  daily notes, templates, and plugin/theme/dev operations. Also use for
  `eval`-based scripting against Obsidian's live `app` object (metadataCache,
  processFrontMatter, resolvedLinks). Trigger on any "go into my vault and do X"
  request, on vault health checks, and on Obsidian plugin/theme debugging.
  Skip for plain file reads/edits at a known path (Read/Edit are faster) and for
  conceptual questions about Obsidian's GUI.
---

# Obsidian CLI

The official CLI is a **remote control for a running Obsidian instance** — not a headless
tool. It talks to the desktop app over IPC, so the app must be running (it is launched
automatically if not).

> Full per-command parameter tables: `references/command-reference.md`.
> The always-authoritative source is `obsidian help` / `obsidian help <command>` — run it
> when a flag is in doubt; your installed version may differ from the online docs.

## Environment it expects (checked against Obsidian 1.13.7)

| Fact | Value |
|---|---|
| App version (auto-updated `.asar`) | 1.13.7 in this reference |
| Installer version (`C:\Program Files\Obsidian\`) | must match the app version, otherwise the CLI prints an upgrade nag |
| CLI enabled | `%APPDATA%\obsidian\obsidian.json` → `"cli": true` |
| `Obsidian.com` (CLI redirector) | present, `C:\Program Files\Obsidian\Obsidian.com` |
| Bash-tool `obsidian` | point a `~/bin/obsidian` wrapper at `Obsidian.com` (see below) |
| PowerShell `obsidian` | resolves to `Obsidian.com` natively (PATHEXT puts `.COM` first) |
| Command surface | all **109** commands of 1.13.7 usable, stderr clean |

## Invocation

Windows ships **two** entry points in the install directory, and only one is the CLI:

- `Obsidian.com` — the CLI redirector. Handles stdin/stdout properly. **Use this.**
- `Obsidian.exe` — the GUI binary. Answers simple commands, but **exits 127 with no output
  and no side effect** for any colon command that carries an argument
  (`property:read name=…`, `daily:append content=…`, `plugins:enabled versions`).

Git Bash resolves a bare `obsidian` by appending `.exe` first, so it would hit the wrong
one. A wrapper fixes it permanently — `~/bin` is already first on the Bash tool's PATH:

```sh
# ~/bin/obsidian  (chmod +x)
#!/bin/sh
exec "/c/Program Files/Obsidian/Obsidian.com" "$@"
```

With that in place, plain `obsidian <command>` works from the Bash tool. If it ever goes
missing, `obsidian property:read name=title path="wiki/index.md"` exits 127 — recreate the
wrapper, or call `"/c/Program Files/Obsidian/Obsidian.com"` by full path.

Prefer the **Bash tool** for pipelines and exit codes. PowerShell also resolves to
`Obsidian.com` correctly now, but still wraps native stderr in `NativeCommandError`.

Output is clean — no banner, no stderr noise, no leading blank line — so no filtering
helper is needed. Wrap calls in `timeout 25` if Obsidian may still be starting up.

## Syntax

```bash
obsidian [vault=<name>] <command> [key=value ...] [flags]
```

- **Parameters** take a value: `content="hello world"`. Quote anything with spaces.
- **Flags** are bare switches: `total`, `overwrite`, `counts`, `permanent`, `verbose`.
- Use `\n` / `\t` inside `content=` for newlines and tabs.
- `--copy` on any command copies the output to the clipboard.
- Chinese arguments and output work correctly through the Bash tool.

### File targeting

Most commands default to the **active file in the UI** when neither is given — never rely
on that from an agent, always pass one:

- `path=<vault-relative path>` — exact, includes the extension: `path="wiki/index.md"`
- `file=<name>` — resolves like a wikilink (bare name, no folder, no `.md`); prints
  `Error: File "X" not found.` **and still exits 0** if the name is ambiguous or missing

### Vault targeting

With exactly one vault registered, `vault=` is optional. Pass `vault="<vault name>"` first
as soon as a second vault exists — otherwise commands silently hit the most recently
focused vault.

## When to use the CLI vs Read/Edit/Grep

Reach for the CLI **only** when you need Obsidian's index or live app state. Everything
else is faster and more precise with the built-in tools (each CLI call costs ~1–2s of IPC).

**CLI wins — no built-in equivalent:**

| Need | Command |
|---|---|
| Incoming links to a note | `backlinks path=… counts format=json` |
| Notes nothing links to / that link nowhere | `orphans total`, `deadends total` |
| Broken wikilinks vault-wide | `unresolved counts verbose format=json` |
| Tag inventory with counts | `tags counts sort=count format=json` |
| Files carrying one tag | `tag name="国际机票" verbose` |
| Every task in the vault | `tasks todo verbose format=json` |
| Frontmatter of a note, parsed | `properties path=… format=json` |
| Which notes use a property, how often | `properties counts sort=count` |
| Heading tree of a note | `outline path=… format=json` |
| Aliases across the vault | `aliases verbose` |
| Word / character count | `wordcount path=…` |
| Search through Obsidian's index (aliases, metadata) | `search query=… limit=… format=json` |
| Rows a `.base` view resolves to | `base:query path=… format=paths` |
| Live app state / arbitrary scripting | `eval code=…` |

**Built-in tools win:**

- Reading a file at a known path → `Read` (offset/limit, no IPC cost)
- **Any content edit** → `Edit`. The CLI has *no* edit command — only
  `append` / `prepend` / `create … overwrite`.
- Regex search, or several lines of surrounding context → `Grep` (`search:context` gives
  one matching line each, index-aware but not regex)
- Non-markdown files, scripts, configs
- Anything that must still work when Obsidian is closed

## Quick reference

```bash
# Read / write
obsidian read path="wiki/index.md"
obsidian create path="ai-output/temporary/drafts/note.md" content="# 标题\n\n正文" overwrite
obsidian append  path="ai-output/temporary/drafts/note.md" content="追加的一行"
obsidian prepend path="ai-output/temporary/drafts/note.md" content="置顶行"   # lands after frontmatter
obsidian move   path="old/note.md" to="new/note.md"       # updates wikilinks if enabled in settings
obsidian rename path="old/note.md" name="新名字"           # extension kept automatically
obsidian delete path="old/note.md"                        # to vault trash; add `permanent` to skip it

# Discovery
obsidian files folder="wiki/concepts" total
obsidian folders folder="产品文档"
obsidian file path="CLAUDE.md"                            # size + created/modified timestamps
obsidian search query="航司联盟" limit=10 format=json
obsidian recents

# Graph & metadata
obsidian backlinks path="wiki/concepts/舱位产品.md" counts
obsidian links path="CLAUDE.md" total
obsidian unresolved counts
obsidian properties path="wiki/index.md" format=json
obsidian tags counts sort=count

# Tasks
obsidian tasks todo total
obsidian tasks path="产品文档/国际机票产品需求/需求.md" verbose   # path + line numbers
obsidian task path="产品文档/国际机票产品需求/需求.md" line=244 toggle

# Properties & daily notes
obsidian property:read name=title path="wiki/index.md"
obsidian property:set  name=status value=draft path="ai-output/temporary/drafts/note.md"
obsidian daily:read
obsidian daily:append content="- [ ] 新任务"     # creates today's note if absent

# Bases & context search
obsidian base:query path="产品工作看板.base" format=paths
obsidian search:context query="航司联盟" limit=5   # grep-style path:line: text

# Escape hatches
obsidian eval code="app.vault.getMarkdownFiles().length"
obsidian command id=editor:toggle-spellcheck
```

## Two gotchas that survive the fixed setup

- **`properties path=… format=json` beats `property:read`** when you want the whole
  frontmatter at once — arrays come back as arrays.
- **`property:set` writes the value verbatim.** `value="[a, b]"` becomes the literal string
  `"[a, b]"`. Pass `type=list|number|checkbox|date|datetime`, or build the value in code
  with `eval` + `processFrontMatter` (below).

## eval — the escape hatch

`eval` runs one line of JavaScript inside the app with `app` in scope, awaits a returned
promise, and prints `=> <result>`. It reaches everything the dedicated commands cannot —
computed frontmatter, the raw link graph, plugin internals.

```bash
# Real YAML types in frontmatter — strings, arrays, booleans, numbers
obsidian eval code="app.fileManager.processFrontMatter(app.vault.getAbstractFileByPath('p/n.md'), f => { f.status='draft'; f.tags=['国际机票','支付']; }).then(() => 'done')"

# Parsed metadata without touching disk
obsidian eval code="JSON.stringify(app.metadataCache.getCache('wiki/index.md').frontmatter)"

# Outgoing resolved links of a note
obsidian eval code="Object.keys(app.metadataCache.resolvedLinks['CLAUDE.md'] || {}).join(', ')"
```

Constraints:

- **Single expression, no top-level `await`.** Chain `.then(() => 'done')` instead — the
  returned promise is awaited for you. A bare `await` fails with
  `Error: await is only valid in async functions…`.
- Quote carefully: wrap `code=` in double quotes and use single quotes inside the JS.
- Multi-line scripts: write to the scratchpad and pass `code="$(cat /path/script.js)"`,
  keeping the whole thing one expression.

Use `property:set type=list` for a simple literal list; reach for `processFrontMatter` when
the value is computed, when several keys change at once, or when you need types
`property:set` cannot express.

## Do not run unattended

These change global state or interrupt the user's session — ask first:
`restart`, `reload`, `devtools`, `plugins:restrict`, `plugin:install` / `plugin:uninstall`,
`theme:set` / `theme:install` / `theme:uninstall`, `sync on|off`, `sync:restore`,
`history:restore`, `publish:add` / `publish:remove`, `delete … permanent`,
`workspace:load`.

`delete` without `permanent` goes to the vault trash and is recoverable.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| exit 127, no output, no effect, on a colon command with arguments | the call reached `Obsidian.exe`, not `Obsidian.com` | restore `~/bin/obsidian` (§ Invocation), or use the full `Obsidian.com` path |
| `Your Obsidian installer is out of date` on every call | app auto-updated past the installer | reinstall from <https://obsidian.md/download>; `obsidian version` shows both numbers |
| `Error: File "X" not found.` **with exit 0** | `file=` name ambiguous or missing | switch to `path=` with the full vault-relative path |
| Command silently targets the wrong note | no `file=`/`path=`, so it used the active UI file | always pass `path=` |
| `NativeCommandError` / mangled exit code | invoked from the PowerShell tool | re-run through the Bash tool |
| `Error: Active file is not a base file` | `base:views` / `base:query` without `path=` | pass `path="<name>.base"` |
| `Error: No template folder configured.` | Templates core plugin has no folder set | set it in Settings, or skip `template=` |
| `Error: Debugger not attached` on `dev:console` | CDP debugger off | run `dev:debug on` first — it alters the running app, so ask before doing it |
| Hangs | Obsidian not running and slow to launch | start Obsidian first; wrap calls in `timeout 25` |

## Plugin / theme development

```bash
obsidian plugin:reload id=my-plugin       # 1. reload after a code change
obsidian dev:errors                       # 2. check for exceptions
obsidian dev:screenshot path=shot.png     # 3. visual check
obsidian dev:debug on                     # 4. attach CDP, then:
obsidian dev:console level=error          #    console output
obsidian dev:dom selector=".workspace-leaf" text
```

`dev:errors` is useful on its own for diagnosing a misbehaving community plugin — it
reports live exceptions with stack traces.

## Attribution

Derived from [`kepano/obsidian-skills`](https://github.com/kepano/obsidian-skills/tree/main/skills/obsidian-cli) (MIT, Copyright (c) 2026 Steph Ango). Modified in this repo; the upstream licence is included as `LICENSE`.
