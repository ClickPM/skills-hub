# Obsidian CLI — Full Command Reference

Generated from `obsidian help` on **Obsidian 1.13.7**, then annotated with observed
behaviour. Online docs: <https://help.obsidian.md/cli>.

> The CLI's own `obsidian help <command>` always beats this file. Regenerate this reference
> after an Obsidian upgrade:
> ```bash
> obsidian help 2>/dev/null > /tmp/obsidian-help.txt
> ```

## Legend

- Every command below was **verified working** on app 1.13.7 with a matching installer,
  invoked through `Obsidian.com` — see `SKILL.md` § Environment it expects.
- Commands default to the **active UI file** when `file=`/`path=` is omitted — always pass
  `path=` from an agent.
- A colon command that exits **127 with no output** means the call went to `Obsidian.exe`
  instead of `Obsidian.com`; see `SKILL.md` § Invocation.

## Global

```
obsidian [vault=<name>] <command> [key=value ...] [flags]

  vault=<name>          Target a specific vault by name (first parameter)
  --copy                Copy this command's output to the clipboard
```

Notes:
- `file=` resolves by name like a wikilink; `path=` is exact (`folder/note.md`).
- Quote values with spaces: `name="My Note"`.
- `\n` = newline, `\t` = tab inside `content=` values.
- Running `obsidian` with no arguments starts the interactive TUI (Tab autocomplete, Ctrl+R
  history search) in a real terminal. Under the Bash tool stdin is not a TTY, so it just
  prints this help and exits — harmless, but useless.
- 109 commands in 1.13.7.

---

## Files & folders

```
  file                  Show file info (path, name, extension, size, created, modified)
    file=<name>  path=<path>

  files                 List files in the vault
    folder=<path>       - Filter by folder
    ext=<extension>     - Filter by extension
    total               - Return file count

  folder                Show folder info
    path=<path>         - Folder path (required)
    info=files|folders|size  - Return specific info only

  folders               List folders in the vault
    folder=<path>       - Filter by parent folder
    total               - Return folder count

  read                  Read file contents
    file=<name>  path=<path>

  create                Create a new file
    name=<name>         - File name
    path=<path>         - File path
    content=<text>      - Initial content
    template=<name>     - Template to use
    overwrite           - Overwrite if file exists
    open                - Open file after creating
    newtab              - Open in new tab

  append                Append content to a file
    content=<text>      - Content to append (required)
    file=<name>  path=<path>
    inline              - Append without newline

  prepend               Prepend content to a file (after frontmatter)
    content=<text>      - Content to prepend (required)
    file=<name>  path=<path>
    inline              - Prepend without newline

  move                  Move or rename a file
    to=<path>           - Destination folder or path (required)
    file=<name>  path=<path>

  rename                Rename a file
    name=<name>         - New file name (required)
    file=<name>  path=<path>

  delete                Delete a file
    file=<name>  path=<path>
    permanent           - Skip trash, delete permanently

  open                  Open a file
    file=<name>  path=<path>
    newtab              - Open in new tab

  recents               List recently opened files
    total               - Return recent file count

  random                Open a random note
    folder=<path>  newtab

  random:read           Read a random note
```

Verified:
- `create path="a/b/c.md"` works with the extension included; parent folders must exist.
- `move` updates wikilinks when "Automatically update internal links" is on in Settings.
- There is **no edit command** — to change existing content use the `Edit` tool, or
  `create … overwrite` to replace the file wholesale.

---

## Search

```
  search                Search vault for text
    query=<text>        - Search query (required)
    path=<folder>       - Limit to folder
    limit=<n>           - Max files
    total               - Return match count
    case                - Case sensitive
    format=text|json    - Output format (default: text)

  search:context        Search with matching line context
    query=<text>  path=<folder>  limit=<n>  case  format=text|json

  search:open           Open search view
    query=<text>
```

Verified:
- Chinese queries work (`search query="航司联盟" total` → 14).
- `format=json` returns a flat JSON array of vault-relative paths.
- `search:context` prints grep-style `path:line: text` — Obsidian-index-aware, but `Grep`
  is still better when you need a regex or several lines of surrounding context.

---

## Links & graph

```
  backlinks             List backlinks to a file
    file=<name>  path=<path>
    counts              - Include link counts
    total               - Return backlink count
    format=json|tsv|csv - Output format (default: tsv)

  links                 List outgoing links from a file
    file=<name>  path=<path>  total

  unresolved            List unresolved links in vault
    total  counts  verbose
    format=json|tsv|csv - Output format (default: tsv)

  orphans               List files with no incoming links
    total               - Return orphan count
    all                 - Include non-markdown files

  deadends              List files with no outgoing links
    total  all

  outline               Show headings for a file
    file=<name>  path=<path>
    format=tree|md|json - Output format (default: tree)
    total               - Return heading count
```

`stats` reports files, folders, markdown notes, orphans, unresolved links and tasks —
take a baseline right after install so later runs have something to compare against.

---

## Properties, tags, aliases

```
  properties            List properties in the vault
    file=<name>  path=<path>   - Show properties for one file
    name=<name>         - Get specific property count
    total  counts  active
    sort=count          - Sort by count (default: name)
    format=yaml|json|tsv  - Output format (default: yaml)

  property:read         Read a property value from a file
    name=<name> (required)  file=<name>  path=<path>

  property:set          Set a property on a file
    name=<name> (required)  value=<value> (required)
    type=text|list|number|checkbox|date|datetime
    file=<name>  path=<path>

  property:remove       Remove a property from a file
    name=<name> (required)  file=<name>  path=<path>

  aliases               List aliases in the vault
    file=<name>  path=<path>  total  verbose  active

  tags                  List tags in the vault
    file=<name>  path=<path>
    total  counts  active
    sort=count          - Sort by count (default: name)
    format=json|tsv|csv - Output format (default: tsv)

  tag                   Get tag info
    name=<tag>          - Tag name (required)
    total  verbose      - verbose includes the file list
```

Verified:
- `property:read name=title path="wiki/index.md"` → `Wiki 主索引`.
- `properties path="wiki/index.md" format=json` dumps the whole frontmatter parsed, arrays
  intact — usually more useful than reading one key at a time.
- `property:set` writes the value **verbatim**, so `value="[a, b]"` lands as the literal
  string `"[a, b]"`. Pass `type=list|number|checkbox|date|datetime` for a real type, or use
  `eval` + `processFrontMatter` (see `SKILL.md` § eval) when building the value in code.

---

## Tasks

```
  tasks                 List tasks in the vault
    file=<name>  path=<path>   - Filter by file
    total  done  todo  active  daily
    status="<char>"     - Filter by status character
    verbose             - Group by file with line numbers
    format=json|tsv|csv - Output format (default: text)

  task                  Show or update a task
    ref=<path:line>     - Task reference (path:line)
    file=<name>  path=<path>  line=<n>
    toggle  done  todo  daily
    status="<char>"     - Set status character
```

Verified: `tasks verbose` is the only form that emits line numbers — you need them to
address a task with `task path=… line=…`.

---

## Daily notes

```
  daily                 Open daily note
    paneType=tab|split|window

  daily:path            Get daily note path
  daily:read            Read daily note contents

  daily:append          Append content to daily note
    content=<text> (required)  inline  open  paneType=…

  daily:prepend         Prepend content to daily note
    content=<text> (required)  inline  open  paneType=…
```

Verified: `daily:path` returns a vault-relative path (e.g. `2026-08-25.md` when daily notes
live at the vault root). `daily:append content="…"` **creates today's note if it does not yet
exist**, so it is not a read-only probe — don't call it just to test the CLI.

---

## Templates

```
  templates             List templates
    total

  template:read         Read template content
    name=<template> (required)  resolve  title=<title>

  template:insert       Insert template into active file
    name=<template> (required)
```

Notes: `resolve` expands `{{date}}`, `{{time}}`, `{{title}}`. `template:insert` targets the
active UI file — for CLI-driven creation use `create path=… template=…` instead. This vault
currently has **no template folder configured**, so `templates` returns
`Error: No template folder configured.`

---

## Bases

```
  bases                 List all base files in vault
  base:views            List views in the current base file

  base:create           Create a new item in a base
    file=<name>  path=<path>  view=<name>  name=<name>  content=<text>  open  newtab

  base:query            Query a base and return results
    file=<name>  path=<path>  view=<name>
    format=json|csv|tsv|md|paths  - Output format (default: json)
```

Verified: this vault has `wiki/Wiki概念库.base` and `产品工作看板.base`.
`base:query path="产品工作看板.base" format=paths` returns the matching note paths.
Without `file=`/`path=` both commands operate on the **active UI file** and fail with
`Error: Active file is not a base file: <current note>` — always pass `path=`.

---

## Bookmarks

```
  bookmarks             List bookmarks
    total  verbose
    format=json|tsv|csv - Output format (default: tsv)

  bookmark              Add a bookmark
    file=<path>  subpath=<subpath>  folder=<path>  search=<query>  url=<url>  title=<title>
```

---

## Commands & hotkeys

```
  commands              List available commands
    filter=<prefix>     - Filter by ID prefix

  command               Execute an Obsidian command
    id=<command-id>     - Command ID to execute (required)

  hotkeys               List hotkeys
    total  verbose  all
    format=json|tsv|csv - Output format (default: tsv)

  hotkey                Get hotkey for a command
    id=<command-id> (required)  verbose
```

`command id=…` is a second escape hatch next to `eval`: anything with a command-palette
entry can be fired from the CLI. `commands filter=editor:toggle` shows the ID namespace.

---

## Plugins, themes, snippets

```
  plugins               List installed plugins
    filter=core|community  versions  format=json|tsv|csv

  plugins:enabled       List enabled plugins
    filter=core|community  versions  format=json|tsv|csv

  plugins:restrict      Toggle or check restricted mode
    on  off

  plugin                Get plugin info
    id=<plugin-id> (required)

  plugin:enable         Enable a plugin
  plugin:disable        Disable a plugin
    id=<id> (required)  filter=core|community

  plugin:install        Install a community plugin
    id=<id> (required)  enable
  plugin:uninstall      Uninstall a community plugin
    id=<id> (required)
  plugin:reload         Reload a plugin (for developers)
    id=<id> (required)

  themes                List installed themes
    versions
  theme                 Show active theme or get info
    name=<name>
  theme:set             Set active theme
    name=<name> (required, empty for default)
  theme:install         Install a community theme
    name=<name> (required)  enable
  theme:uninstall       Uninstall a theme
    name=<name> (required)

  snippets              List installed CSS snippets
  snippets:enabled      List enabled CSS snippets
  snippet:enable        Enable a CSS snippet
  snippet:disable       Disable a CSS snippet
    name=<name> (required)
```

`plugins:enabled versions format=json` is the quickest inventory of what is actually
running; `plugin id=<id>` reports one plugin's state. Enable/disable/install/uninstall
change the user's environment — see `SKILL.md` § Do not run unattended.

---

## File history, diff, sync, publish

```
  history               List file history versions
    file=<name>  path=<path>
  history:list          List files with history
  history:read          Read a file history version
    file=<name>  path=<path>  version=<n> (default: 1)
  history:restore       Restore a file history version
    version=<n> (required)  file=<name>  path=<path>
  history:open          Open file recovery UI

  diff                  List or diff local/sync versions
    file=<name>  path=<path>  from=<n>  to=<n>  filter=local|sync

  sync                  Pause or resume sync
    on  off
  sync:status           Show sync status
  sync:deleted          List deleted files in sync
  sync:history          List sync version history for a file
  sync:read             Read a sync version
  sync:restore          Restore a sync version
  sync:open             Open sync history UI

  publish:site          Show publish site info
  publish:list          List published files
  publish:status        List publish changes
  publish:add           Publish a file or all changed files
  publish:remove        Unpublish a file
  publish:open          Open file on published site
```

Verified: Sync is **not set up** for this vault (`sync:status` → `disconnected`) and
Publish is not configured (`publish:site` returns empty), so the whole `sync:*` / `publish:*`
surface is inert here. `history:list` / `history` / `diff` do work and are the entry point
into Obsidian's local file recovery — a second safety net next to git.

---

## Workspace, tabs, vault, system

```
  workspace             Show workspace tree
    ids                 - Include workspace item IDs

  tabs                  List open tabs
    ids
  tab:open              Open a new tab
    group=<id>  file=<path>  view=<type>

  vault                 Show vault info
    info=name|path|files|folders|size
  vaults                List known vaults
    total  verbose

  version               Show Obsidian version   →  "1.13.7 (installer 1.13.7)"
  reload                Reload the vault
  restart               Restart the app

  wordcount             Count words and characters
    file=<name>  path=<path>  words  characters
```

`version` is the fastest health check: it prints the app version **and** the installer
version. If the two diverge again after an auto-update, the installer is stale and Obsidian
appends a "your installer is out of date" warning to every command's output.

---

## Developer

```
  eval                  Execute JavaScript and return result
    code=<javascript>   - JavaScript code to execute (required)

  devtools              Toggle Electron dev tools

  dev:errors            Show captured errors
    clear
  dev:console           Show captured console messages
    clear  limit=<n> (default 50)  level=log|warn|error|info|debug
  dev:debug             Attach/detach CDP debugger
    on  off
  dev:cdp               Run a Chrome DevTools Protocol command
    method=<CDP.method> (required)  params=<json>
  dev:css               Inspect CSS with source locations
    selector=<css> (required)  prop=<name>
  dev:dom               Query DOM elements
    selector=<css> (required)  total  text  inner  all  attr=<name>  css=<prop>
  dev:screenshot        Take a screenshot
    path=<filename>
  dev:mobile            Toggle mobile emulation
    on  off
```

Verified:
- `eval` awaits a returned promise and prints `=> <result>`. Top-level `await` is a syntax
  error, so chain `.then(...)` instead.
- `dev:errors` reports live plugin exceptions with stack traces — useful on its own for
  diagnosing a misbehaving community plugin.
- `dev:console` returns `Error: Debugger not attached.` until you run `dev:debug on`.
  Attaching the CDP debugger changes the running app's state, so ask before doing it.

---

## Commands documented online but absent in 1.13.7

`obsidian help` on 1.13.7 does **not** list these, although help.obsidian.md describes
them — do not plan around them without checking `obsidian help` first:
`unique`, `web`, `workspaces`, `workspace:save`, `workspace:load`, `workspace:delete`,
`vault:open` (TUI only).
