"""Git 版本管理 Schemas"""
from pydantic import BaseModel, Field
from typing import Optional


class GitStatusItem(BaseModel):
    path: str
    status: str  # M/A/D/R/?
    staged: bool = False


class GitCommitRequest(BaseModel):
    message: str = Field(..., min_length=1)
    paths: list[str] = Field(default_factory=list)
    author: Optional[str] = None


class GitBranchInfo(BaseModel):
    current: str
    branches: list[str]


class GitLogEntry(BaseModel):
    hash: str
    author: str
    date: str
    message: str


class GitDiffRequest(BaseModel):
    file: str = ""
    from_hash: Optional[str] = None
    to_hash: Optional[str] = None


class GitRestoreRequest(BaseModel):
    file: str
    version: Optional[str] = None


class GitWorkspaceInitRequest(BaseModel):
    path: str = "."


class GitRemoteRequest(BaseModel):
    url: str
    name: str = "origin"
