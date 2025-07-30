from __future__ import annotations
import os
import pathlib
import re
import subprocess
from typing import Iterable, Sequence

# -------- Git helpers ---------


def git_repo_root(path: pathlib.Path) -> pathlib.Path | None:
    try:
        out = subprocess.check_output(
            ["git", "-C", str(path), "rev-parse", "--show-toplevel"],
            stderr=subprocess.DEVNULL,
        )
        return pathlib.Path(out.decode().strip())
    except Exception:
        return None


def git_changed_files(repo_root: pathlib.Path, staged: bool = False) -> set[str]:
    cmd = ["git", "-C", str(repo_root), "diff", "--name-only"]
    if staged:
        cmd.append("--cached")
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL)
        return {p.replace("\\", "/") for p in out.decode().splitlines() if p.strip()}
    except subprocess.CalledProcessError:
        return set()


# -------- Path helpers ---------


def rel_path(path: str | pathlib.Path, base: pathlib.Path) -> str:
    return os.path.relpath(path, base).replace("\\", "/")


def parent_dir_name(rel: str) -> str:
    return pathlib.Path(rel).parent.name


# -------- Matching helpers -----


def _ensure_iter(x: Sequence[str] | None) -> list[str]:
    return list(x or [])


def match_any(
    patterns: Iterable[str], value: str, regex: bool, mode: str = "any"
) -> bool:
    """Return True if *any* pattern matches value. modes: start|end|any."""
    for pat in patterns:
        if regex:
            try:
                if mode == "start" and re.match(pat, value):
                    return True
                if mode == "end" and re.search(f"{pat}$", value):
                    return True
                if mode == "any" and re.search(pat, value):
                    return True
            except re.error:
                continue
        else:
            if mode == "start" and value.startswith(pat):
                return True
            if mode == "end" and value.endswith(pat):
                return True
            if mode == "any" and pat in value:
                return True
    return False
