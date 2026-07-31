"""Git 版本管理控制器 — 对本地 Git 仓库的操作封装"""
import asyncio
import os
import subprocess
from pathlib import Path
from typing import Any, Optional

import structlog

from config.db import get_settings

LOGGER = structlog.get_logger(__name__)


class GitController:
    """Git 操作封装：status / history / diff / commit / restore / workspace"""

    GIT_BIN = "git"

    @staticmethod
    def _get_repo_path(sub_path: str = "") -> str:
        settings = get_settings()
        base = getattr(settings, "PROJECT_ROOT", ".")
        return str(Path(base) / sub_path) if sub_path else base

    @staticmethod
    async def _run_git(args: list[str], cwd: str = ".") -> tuple[str, str]:
        """执行 git 命令，返回 (stdout, stderr)

        注意：使用线程池 + 同步 subprocess.run，而不是 asyncio.create_subprocess_exec。
        因为 uvicorn[standard] 的 httptools 在 Windows 上强制 SelectorEventLoop，
        该 loop 不支持子进程（_make_subprocess_transport 抛 NotImplementedError）。
        """
        result = await asyncio.to_thread(
            subprocess.run,
            [GitController.GIT_BIN, *args],
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        return result.stdout, result.stderr

    @staticmethod
    async def status(cwd: str = ".") -> dict[str, Any]:
        stdout, _ = await GitController._run_git(["status", "--porcelain"], cwd)
        branch_stdout, _ = await GitController._run_git(["branch", "--show-current"], cwd)
        items = []
        for line in stdout.splitlines():
            if len(line) > 3:
                status_code = line[:2].strip()
                path = line[3:].strip()
                items.append({"path": path, "status": status_code, "staged": line[0] != " " and line[0] != "?"})
        return {"branch": branch_stdout.strip(), "changes": items, "dirty": len(items) > 0}

    @staticmethod
    async def log(max_count: int = 20, cwd: str = ".") -> list[dict[str, str]]:
        stdout, _ = await GitController._run_git(
            ["log", f"--max-count={max_count}", "--format=%H||%an||%ai||%s"], cwd
        )
        entries = []
        for line in stdout.splitlines():
            parts = line.split("||", 3)
            if len(parts) == 4:
                entries.append({"hash": parts[0], "author": parts[1], "date": parts[2], "message": parts[3]})
        return entries

    @staticmethod
    async def diff(file: str = "", from_hash: Optional[str] = None, to_hash: Optional[str] = None, cwd: str = ".") -> str:
        args = ["diff"]
        if from_hash:
            args.append(from_hash)
        if to_hash:
            args.append(to_hash)
        if file:
            args.append("--", file)
        stdout, _ = await GitController._run_git(args, cwd)
        return stdout

    @staticmethod
    async def commit(message: str, paths: list[str] | None = None, cwd: str = ".") -> dict[str, Any]:
        if paths:
            await GitController._run_git(["add"] + paths, cwd)
        else:
            await GitController._run_git(["add", "-A"], cwd)
        stdout, stderr = await GitController._run_git(["commit", "-m", message], cwd)
        msg = stdout.strip() or stderr.strip()
        return {"message": msg}

    @staticmethod
    async def restore(file: str, version: Optional[str] = None, cwd: str = ".") -> bool:
        if version:
            stdout, _ = await GitController._run_git(["checkout", version, "--", file], cwd)
        else:
            stdout, _ = await GitController._run_git(["restore", file], cwd)
        return True

    @staticmethod
    async def init_workspace(path: str, cwd: str = ".") -> dict[str, Any]:
        target = str(Path(cwd) / path) if path != "." else cwd
        os.makedirs(target, exist_ok=True)
        stdout, _ = await GitController._run_git(["init"], target)
        LOGGER.bind(path=target).info("Git workspace initialized")
        return {"path": target, "message": stdout.strip()}

    @staticmethod
    async def set_remote(url: str, name: str = "origin", cwd: str = ".") -> dict[str, Any]:
        stdout, _ = await GitController._run_git(["remote", "add", name, url], cwd)
        return {"message": f"Remote {name} added: {url}"}

    @staticmethod
    async def push(remote: str = "origin", branch: str = "main", cwd: str = ".") -> dict[str, Any]:
        stdout, _ = await GitController._run_git(["push", remote, branch], cwd)
        return {"message": stdout.strip()}

    @staticmethod
    async def fetch(cwd: str = ".") -> dict[str, Any]:
        stdout, _ = await GitController._run_git(["fetch"], cwd)
        return {"message": stdout.strip()}

    @staticmethod
    async def show_file(path: str, version: str = "HEAD", cwd: str = ".") -> str:
        """读取指定版本 (默认 HEAD) 下某个文件的内容"""
        stdout, stderr = await GitController._run_git(["show", f"{version}:{path}"], cwd)
        return stdout
