/**
 * ProjectDashboard — 项目仪表盘
 *
 * 展示项目概览：原型总数、标注覆盖率、发布通道状态、最近活动。
 */

import { useCallback, useEffect, useState } from 'react';
import {
    Activity,
    CheckCircle2,
    Clock,
    ExternalLink,
    Globe,
    Loader2,
    RefreshCw,
    Server,
    XCircle,
} from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';

/* ─── Types ─────────────────────────────────────────── */

interface ChannelInfo {
    id: string;
    name: string;
    type: string;
    baseUrl?: string;
    currentVersion?: number;
    status: string;
    publishedAt?: number;
}

interface PublishRecord {
    id: string;
    channelId: string;
    version: number;
    summary: string;
    status: string;
    createdAt: number;
}

interface DashboardData {
    channels: ChannelInfo[];
    latestRecords: PublishRecord[];
    totalDeploys: number;
}

/* ─── Component ─────────────────────────────────────── */

interface ProjectDashboardProps {
    projectId: string;
    serverUrl?: string;
}

const statusIcon: Record<string, { icon: React.ComponentType<{ size?: number }>; color: string; label: string }> = {
    published: { icon: CheckCircle2, color: '#52c41a', label: '已发布' },
    pending: { icon: Clock, color: '#8c8c8c', label: '未发布' },
    publishing: { icon: Loader2, color: '#1677ff', label: '发布中' },
    failed: { icon: XCircle, color: '#ff4d4f', label: '失败' },
};

const typeLabel: Record<string, string> = {
    development: '开发',
    review: '评审',
    production: '正式',
};

function fmtTime(ts?: number): string {
    if (!ts) return '-';
    const d = new Date(ts);
    return `${d.getMonth() + 1}/${d.getDate()} ${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`;
}

export default function ProjectDashboard({ projectId, serverUrl }: ProjectDashboardProps) {
    const [data, setData] = useState<DashboardData | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const baseUrl = serverUrl || '';

    const loadDashboard = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const res = await fetch(`${baseUrl}/api/publish/dashboard?projectId=${encodeURIComponent(projectId)}`);
            const json = await res.json();
            if (json.ok) setData(json);
            else setError(json.error || '加载失败');
        } catch (e) {
            setError(String(e));
        } finally {
            setLoading(false);
        }
    }, [baseUrl, projectId]);

    useEffect(() => { void loadDashboard(); }, [loadDashboard]);

    return (
        <div className="space-y-4 rounded-lg border border-border bg-background p-4">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-sm font-medium">
                    <Activity size={16} />
                    项目概览
                </div>
                <Button variant="ghost" size="icon" className="h-7 w-7" onClick={loadDashboard}>
                    <RefreshCw size={13} className={loading ? 'animate-spin' : ''} />
                </Button>
            </div>

            {loading && !data ? (
                <div className="py-8 text-center text-xs text-muted-foreground">
                    <Loader2 size={16} className="mx-auto mb-2 animate-spin" />
                    加载中...
                </div>
            ) : error ? (
                <div className="py-8 text-center text-xs text-red-400">{error}</div>
            ) : !data ? (
                <div className="py-8 text-center text-xs text-muted-foreground">暂无数据</div>
            ) : (
                <>
                    {/* 发布通道 */}
                    <div>
                        <div className="mb-2 flex items-center gap-1.5 text-[11px] font-medium text-muted-foreground">
                            <Globe size={12} />
                            发布通道
                        </div>
                        <div className="space-y-1.5">
                            {data.channels.map((ch) => {
                                const st = statusIcon[ch.status] ?? statusIcon.pending;
                                const Icon = st.icon;
                                return (
                                    <div key={ch.id} className="flex items-center justify-between rounded-md border border-border/50 px-3 py-2 text-xs">
                                        <div className="flex items-center gap-2">
                                            <Icon size={13} style={{ color: st.color }} />
                                            <span className="font-medium">{ch.name}</span>
                                            <span className="rounded bg-muted px-1.5 py-0.5 text-[10px] text-muted-foreground">
                                                {typeLabel[ch.type] ?? ch.type}
                                            </span>
                                            {ch.currentVersion && (
                                                <span className="text-muted-foreground">v{ch.currentVersion}</span>
                                            )}
                                        </div>
                                        <div className="flex items-center gap-2">
                                            {ch.baseUrl && (
                                                <TooltipProvider>
                                                    <Tooltip>
                                                        <TooltipTrigger asChild>
                                                            <a href={ch.baseUrl} target="_blank" rel="noreferrer"
                                                               className="text-muted-foreground hover:text-foreground">
                                                                <ExternalLink size={12} />
                                                            </a>
                                                        </TooltipTrigger>
                                                        <TooltipContent>{ch.baseUrl}</TooltipContent>
                                                    </Tooltip>
                                                </TooltipProvider>
                                            )}
                                            <span className="text-[10px] text-muted-foreground">
                                                {st.label}
                                            </span>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    </div>

                    {/* 最近活动 */}
                    {data.latestRecords.length > 0 && (
                        <div>
                            <div className="mb-2 flex items-center gap-1.5 text-[11px] font-medium text-muted-foreground">
                                <Server size={12} />
                                最近发布
                            </div>
                            <div className="space-y-1">
                                {data.latestRecords.slice(0, 5).map((rec) => {
                                    const ch = data.channels.find((c) => c.id === rec.channelId);
                                    return (
                                        <div key={rec.id} className="flex items-center justify-between rounded-md bg-muted/30 px-3 py-1.5 text-xs">
                                            <div className="flex items-center gap-2">
                                                <span className="font-medium">{ch?.name ?? rec.channelId}</span>
                                                <span className="text-muted-foreground">v{rec.version}</span>
                                                <span className="text-muted-foreground truncate max-w-[200px]">{rec.summary}</span>
                                            </div>
                                            <span className="text-[10px] text-muted-foreground">{fmtTime(rec.createdAt)}</span>
                                        </div>
                                    );
                                })}
                            </div>
                        </div>
                    )}

                    {/* 统计 */}
                    <div className="flex gap-4 text-[11px] text-muted-foreground border-t border-border/50 pt-2">
                        <span>通道: {data.channels.length}</span>
                        <span>总发布: {data.totalDeploys}</span>
                        <span>已发布: {data.channels.filter((c) => c.status === 'published').length}</span>
                    </div>
                </>
            )}
        </div>
    );
}
