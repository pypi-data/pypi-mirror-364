# cbler

> Concatenate code into your clipboard with filters.

**cbler** is a CLI tool for extracting source files, filtering them, and copying the result to your clipboard. It also includes several helpful Git utilities for viewing logs and diffs.

- Built with [Typer](https://typer.tiangolo.com/)
- Rich, colorful output
- Multi-flag filtering with regex support
- Git integration for diffs and logs
- Designed for piping code into LLMs like ChatGPT, Claude, or Gemini

---

## Install

```bash
pip install cbler
```

---

## CLI Layout

```bash
cbler code <lang> [path] [filters]
cbler git log [path] [options]
cbler git diff [path] [options]
cbler git tree [path] [options]
```

--- 

## `code` Command

The `code` command is the core of `cbler`. It walks a directory, finds files matching the specified language (`py` or `gml`), applies a series of filters, and copies the concatenated result to the clipboard.

### Usage

```bash
# Copy all python files in the current directory, excluding test files
cbler code py . --not-suffix _test.py

# Copy all GameMaker scripts containing "Player" in their path
cbler code gml . --path-contains Player

# Copy all python files that have been changed in git (unstaged)
cbler code py . --git-diff
```

### Code Command Filters

All filters are optional and can be combined. They accept multiple values (e.g., `--suffix .py .pyw`) and support regex patterns by default (disable with `--no-regex`).

| Filter | Description |
| --- | --- |
| `--prefix`, `--not-prefix` | Match file names that start with a pattern. |
| `--suffix`, `--not-suffix` | Match file names that end with a pattern. |
| `--contains`, `--not-contains` | Match file names that contain a pattern. |
| `--path-contains`, `--not-path-contains` | Match the full relative path against a pattern. |
| `--parent-contains` | Parent directory must match ANY of the given patterns. |
| `--parent-contains-all` | Parent directory must match ALL of the given patterns. |
| `--git-diff` | Only include files that are part of the unstaged git diff. |
| `--git-staged` | Only include files that have been staged in git. |
| `--no-regex` | Disable regex matching for all filters. |


--- 

## `git` Command

The `git` command provides several utilities for inspecting a Git repository.

### `git log`

Shows a detailed, formatted log of the most recent commits.

```bash
cbler git log . -n 20  # Show last 20 commits
```

### `git diff`

Displays a summary of file changes (modified, added, deleted, untracked). 

```bash
cbler git diff             # Show unstaged changes and untracked files
cbler git diff --staged    # Show only staged changes
cbler git diff --no-untracked # Hide untracked files
```

### `git tree`

Displays a compact, graphical representation of the commit history.

```bash
cbler git tree -n 30  # Show a graph of the last 30 commits
```

---

## Roadmap

- [ ] `--max-files` limit with confirmation
- [ ] Progress bar
- [ ] `--output` for saving to file
- [ ] Show skipped files with reasons

---

## Dev install

```bash
uv pip install -e .
cbler code py . --suffix .py
```

---

## License

MIT

---

## Name

"cbler" = clipboard + -ler
