/**
 * AnnotationVersionPanel — 标注版本管理面板
 *
 * 展示 annotation-source.json 中的版本历史，支持：
 * - 版本时间轴视图
 * - Diff 详情展开
 * - 手动创建版本
 * - 回滚到指定版本
 */

import { useCallback, useEffect, useMemo, useState } from 'react';
import {
    AlertTriangle,
    CheckCircle2,
    GitCommitHorizontal,
    History,
    Loader2,
    Plus,
    RotateCcw,
    X,
} from 'lucide-react';
import { toast } from 'sonner';

import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { withProjectScope } from '../services/projectScope';

/* ─── Types ─────────────────────────────────────────── */

interface AnnotationVersion {
    version: number;
    parentVersion?: number;
    timestamp?: number;
    author?: string;
    summary: string;
    tags?: string[];
    status?: 'draft' | 'review' | 'released';
    diffCount?: number;
}

interface VersionListResponse {
    ok: boolean;
    currentVersion: number;
    versions: AnnotationVersion[];
    error?: string;
}

/* ─── Helpers ────────────────────────────────────────── */

function formatTime(ts?: number): string {
    if (!ts) return '未知时间';
    const d = new Date(ts);
    const pad = (n: number) => String(n).padStart(2, '0');
    return `${d.getFullYear()}/${pad(d.getMonth() + 1)}/${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

function relativeTime(ts?: number): string {
    if (!ts) return '';
    const seconds = Math.max(0, Math.floor((Date.now() - ts) / 1000));
    if (seconds < 60) return '刚刚';
    if (seconds < 3600) return `${Math.floor(seconds / 60)} 分钟前`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)} 小时前`;
    if (seconds < 2592000) return `${Math.floor(seconds / 86400)} 天前`;
    return `${Math.floor(seconds / 2592000)} 个月前`;
}

const statusLabel: Record<string, string> = {
    draft: '草稿',
    review: '评审中',
    released: '已发布',
};

const statusColor: Record<string, string> = {
    draft: '#8c8c8c',
    review: '#1677ff',
    released: '#52c41a',
};

/* ─── Component ──────────────────────────────────────── */

interface AnnotationVersionPanelProps {
    /** 原型路径，例如 "prototypes/my-app" */
    targetPath: string;
    /** 是否显示面板 */
    visible: boolean;
    /** 关闭面板回调 */
    onClose: () => void;
}

export default function AnnotationVersionPanel({
    targetPath,
    visible,
    onClose,
}: AnnotationVersionPanelProps) {
    const [versions, setVersions] = useState<AnnotationVersion[]>([]);
    const [currentVersion, setCurrentVersion] = useState(0);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [expandedVersion, setExpandedVersion] = useState<number | null>(null);
    const [showCreateDialog, setShowCreateDialog] = useState(false);
    const [newVersionSummary, setNewVersionSummary] = useState('');
    const [creating, setCreating] = useState(false);
    const [rollbackTarget, setRollbackTarget] = useState<AnnotationVersion | null>(null);
    const [rollingBack, setRollingBack] = useState(false);
    const [expandedDiffVer, setExpandedDiffVer] = useState<number | null>(null);

    /** 加载版本列表 */
    const loadVersions = useCallback(async () => {
        if (!targetPath) return;
        setLoading(true);
        setError(null);
        try {
            const url = withProjectScope(`/api/prototype-annotation/versions?targetPath=${encodeURIComponent(targetPath)}`);
            const response = await fetch(url);
            const data: VersionListResponse = await response.json();
            if (data.ok && Array.isArray(data.versions)) {
                setVersions(data.versions);
                setCurrentVersion(data.currentVersion);
            } else {
                setError(data.error || '加载失败');
            }
        } catch (err) {
            setError(String(err));
        } finally {
            setLoading(false);
        }
    }, [targetPath]);

    /** 加载数据 */
    useEffect(() => {
        if (visible && targetPath) {
            void loadVersions();
        }
    }, [visible, targetPath, loadVersions]);

    /** 手动创建版本 */
    const handleCreateVersion = useCallback(async () => {
        if (!newVersionSummary.trim()) {
            toast.error('请输入版本说明');
            return;
        }
        setCreating(true);
        try {
            const url = withProjectScope(`/api/prototype-annotation/versions?targetPath=${encodeURIComponent(targetPath)}`);
            const response = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ summary: newVersionSummary.trim(), tags: ['manual'] }),
            });
            const data = await response.json();
            if (data.ok) {
                toast.success(`版本 v${data.version.version} 已创建`);
                setShowCreateDialog(false);
                setNewVersionSummary('');
                void loadVersions();
            } else {
                toast.error(data.error || '创建失败');
            }
        } catch (err) {
            toast.error('创建版本失败: ' + String(err));
        } finally {
            setCreating(false);
        }
    }, [targetPath, newVersionSummary, loadVersions]);

    /** 回滚到指定版本 */
    const handleRollback = useCallback(async () => {
        if (!rollbackTarget) return;
        setRollingBack(true);
        try {
            const url = withProjectScope(
                `/api/prototype-annotation/versions/${rollbackTarget.version}/rollback?targetPath=${encodeURIComponent(targetPath)}`,
            );
            const response = await fetch(url, { method: 'POST' });
            const data = await response.json();
            if (data.ok) {
                toast.success(`已回滚到 v${rollbackTarget.version}`);
                setRollbackTarget(null);
                void loadVersions();
            } else {
                toast.error(data.error || '回滚失败');
            }
        } catch (err) {
            toast.error('回滚失败: ' + String(err));
        } finally {
            setRollingBack(false);
        }
    }, [targetPath, rollbackTarget, loadVersions]);

    /** 版本列表反转（最新在上） */
    const sortedVersions = useMemo(() => [...versions].reverse(), [versions]);

    if (!visible) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-start justify-center bg-black/30 pt-12">
            <div className="w-full max-w-lg rounded-lg border border-border bg-background shadow-xl">
                {/* ─── Header ─── */}
                <div className="flex items-center justify-between border-b border-border px-4 py-3">
                    <div className="flex items-center gap-2 text-sm font-medium">
                        <History size={16} />
                        标注版本历史
                        {currentVersion > 0 && (
                            <span className="text-xs text-muted-foreground">当前: v{currentVersion}</span>
                        )}
                    </div>
                    <div className="flex items-center gap-1">
                        <TooltipProvider>
                            <Tooltip>
                                <TooltipTrigger asChild>
                                    <Button variant="ghost" size="icon" className="h-7 w-7" onClick={loadVersions}>
                                        <Loader2 size={14} className={loading ? 'animate-spin' : ''} />
                                    </Button>
                                </TooltipTrigger>
                                <TooltipContent>刷新</TooltipContent>
                            </Tooltip>
                        </TooltipProvider>
                        <TooltipProvider>
                            <Tooltip>
                                <TooltipTrigger asChild>
                                    <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => setShowCreateDialog(true)}>
                                        <Plus size={14} />
                                    </Button>
                                </TooltipTrigger>
                                <TooltipContent>创建版本</TooltipContent>
                            </Tooltip>
                        </TooltipProvider>
                        <TooltipProvider>
                            <Tooltip>
                                <TooltipTrigger asChild>
                                    <Button variant="ghost" size="icon" className="h-7 w-7" onClick={onClose}>
                                        <X size={14} />
                                    </Button>
                                </TooltipTrigger>
                                <TooltipContent>关闭</TooltipContent>
                            </Tooltip>
                        </TooltipProvider>
                    </div>
                </div>

                {/* ─── Body ─── */}
                <div className="max-h-[70vh] overflow-y-auto p-4">
                    {loading && versions.length === 0 ? (
                        <div className="flex items-center justify-center py-12 text-muted-foreground">
                            <Loader2 size={20} className="animate-spin mr-2" />
                            加载中...
                        </div>
                    ) : error ? (
                        <div className="flex flex-col items-center gap-2 py-8 text-sm text-red-500">
                            <AlertTriangle size={20} />
                            <span>{error}</span>
                            <Button variant="outline" size="sm" onClick={loadVersions}>重试</Button>
                        </div>
                    ) : versions.length === 0 ? (
                        <div className="flex flex-col items-center gap-2 py-8 text-sm text-muted-foreground">
                            <History size={24} />
                            <span>暂无版本记录</span>
                            <span className="text-xs">修改标注后会自动生成版本</span>
                        </div>
                    ) : (
                        <div className="space-y-1">
                            {sortedVersions.map((ver) => (
                                <div key={ver.version}>
                                    {/* 版本卡片 */}
                                    <div
                                        className={[
                                            'group flex items-start gap-3 rounded-md px-3 py-2.5 transition-colors',
                                            'hover:bg-accent/50 cursor-pointer',
                                            ver.version === currentVersion ? 'border border-primary/20 bg-primary/5' : '',
                                        ].join(' ')}
                                        onClick={() => setExpandedDiffVer(expandedDiffVer === ver.version ? null : ver.version)}
                                    >
                                        {/* 时间轴圆点 */}
                                        <div className="mt-1 flex flex-col items-center">
                                            <div
                                                className="h-2.5 w-2.5 rounded-full border-2"
                                                style={{
                                                    borderColor: statusColor[ver.status ?? 'draft'] ?? '#8c8c8c',
                                                    backgroundColor: ver.version === currentVersion ? (statusColor[ver.status ?? 'draft'] ?? '#8c8c8c') : 'transparent',
                                                }}
                                            />
                                        </div>

                                        {/* 内容 */}
                                        <div className="flex-1 min-w-0">
                                            <div className="flex items-center gap-2">
                                                <span className="text-xs font-semibold text-foreground">v{ver.version}</span>
                                                {ver.status && (
                                                    <span
                                                        className="rounded-full px-1.5 py-0.5 text-[10px] font-medium leading-none"
                                                        style={{
                                                            backgroundColor: (statusColor[ver.status] ?? '#8c8c8c') + '1a',
                                                            color: statusColor[ver.status] ?? '#8c8c8c',
                                                        }}
                                                    >
                                                        {statusLabel[ver.status] ?? ver.status}
                                                    </span>
                                                )}
                                                {ver.version === currentVersion && (
                                                    <span className="rounded bg-primary/10 px-1.5 py-0.5 text-[10px] font-medium text-primary">
                                                        当前
                                                    </span>
                                                )}
                                                <span className="ml-auto text-[10px] text-muted-foreground">
                                                    {relativeTime(ver.timestamp)}
                                                </span>
                                            </div>
                                            <p className="mt-0.5 text-xs text-foreground/80 truncate">{ver.summary}</p>
                                            <div className="mt-1 flex items-center gap-3 text-[10px] text-muted-foreground">
                                                <span>{formatTime(ver.timestamp)}</span>
                                                {ver.diffCount !== undefined && (
                                                    <span>{ver.diffCount} 项变更</span>
                                                )}
                                                {ver.parentVersion && (
                                                    <span>基于 v{ver.parentVersion}</span>
                                                )}
                                            </div>
                                        </div>

                                        {/* 操作按钮 */}
                                        <div className="flex shrink-0 items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                            {ver.version < currentVersion && (
                                                <TooltipProvider>
                                                    <Tooltip>
                                                        <TooltipTrigger asChild>
                                                            <Button
                                                                variant="ghost"
                                                                size="icon"
                                                                className="h-7 w-7"
                                                                onClick={(e) => {
                                                                    e.stopPropagation();
                                                                    setRollbackTarget(ver);
                                                                }}
                                                            >
                                                                <RotateCcw size={13} />
                                                            </Button>
                                                        </TooltipTrigger>
                                                        <TooltipContent>回滚到 v{ver.version}</TooltipContent>
                                                    </Tooltip>
                                                </TooltipProvider>
                                            )}
                                        </div>
                                    </div>

                                    {/* 展开的 Diff 详情 */}
                                    {expandedDiffVer === ver.version && (
                                        <div className="ml-7 mb-2 rounded-md border border-border/50 bg-muted/20 px-3 py-2 text-xs">
                                            <div className="flex items-center gap-2 text-muted-foreground mb-1">
                                                <GitCommitHorizontal size={12} />
                                                <span className="font-medium">变更详情</span>
                                            </div>
                                            <p className="text-muted-foreground">
                                                {ver.diffCount && ver.diffCount > 0
                                                    ? `此次版本包含 ${ver.diffCount} 项标注变更。完整的 diff 数据可在服务端查看。`
                                                    : ver.summary}
                                            </p>
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                {/* ─── Footer ─── */}
                <div className="border-t border-border px-4 py-2.5">
                    <p className="text-[10px] text-muted-foreground">
                        每次标注修改自动生成新版本 · 共 {versions.length} 个版本
                    </p>
                </div>
            </div>

            {/* ─── 创建版本对话框 ─── */}
            <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
                <DialogContent className="sm:max-w-md">
                    <DialogHeader>
                        <DialogTitle className="flex items-center gap-2 text-sm">
                            <Plus size={15} />
                            手动创建版本
                        </DialogTitle>
                    </DialogHeader>
                    <div className="space-y-3 py-2">
                        <p className="text-xs text-muted-foreground">
                            创建一个新版本标记，例如 "交付v1"、"评审版"。当前标注内容会被记录为快照。
                        </p>
                        <Input
                            placeholder="输入版本说明（必填）"
                            value={newVersionSummary}
                            onChange={(e) => setNewVersionSummary(e.target.value)}
                            onKeyDown={(e) => {
                                if (e.key === 'Enter' && newVersionSummary.trim()) {
                                    void handleCreateVersion();
                                }
                            }}
                            autoFocus
                        />
                    </div>
                    <DialogFooter>
                        <Button variant="outline" size="sm" onClick={() => setShowCreateDialog(false)}>
                            取消
                        </Button>
                        <Button
                            size="sm"
                            onClick={handleCreateVersion}
                            disabled={!newVersionSummary.trim() || creating}
                        >
                            {creating ? <Loader2 size={14} className="animate-spin mr-1" /> : null}
                            {creating ? '创建中...' : '创建版本'}
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>

            {/* ─── 回滚确认对话框 ─── */}
            <Dialog open={rollbackTarget !== null} onOpenChange={(open) => { if (!open) setRollbackTarget(null); }}>
                <DialogContent className="sm:max-w-md">
                    <DialogHeader>
                        <DialogTitle className="flex items-center gap-2 text-sm">
                            <RotateCcw size={15} />
                            确认回滚
                        </DialogTitle>
                    </DialogHeader>
                    <div className="space-y-2 py-2 text-xs">
                        <div className="flex items-center gap-2 rounded-md bg-amber-50 border border-amber-200 p-3 text-amber-800">
                            <AlertTriangle size={14} className="shrink-0" />
                            <span>回滚操作会创建一个新版本，不会删除已有版本历史。</span>
                        </div>
                        <p>
                            确认回滚到 <strong>v{rollbackTarget?.version}</strong>？
                        </p>
                        {rollbackTarget && (
                            <p className="text-muted-foreground">
                                摘要: {rollbackTarget.summary}
                                <br />
                                时间: {formatTime(rollbackTarget.timestamp)}
                            </p>
                        )}
                    </div>
                    <DialogFooter>
                        <Button variant="outline" size="sm" onClick={() => setRollbackTarget(null)}>
                            取消
                        </Button>
                        <Button
                            variant="destructive"
                            size="sm"
                            onClick={handleRollback}
                            disabled={rollingBack}
                        >
                            {rollingBack ? <Loader2 size={14} className="animate-spin mr-1" /> : null}
                            {rollingBack ? '回滚中...' : '确认回滚'}
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </div>
    );
}
