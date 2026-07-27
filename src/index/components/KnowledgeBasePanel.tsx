/**
 * KnowledgeBasePanel — 知识库管理面板
 *
 * 浏览、搜索、创建、编辑、删除知识条目。
 * 支持按类型筛选和全文搜索。
 */

import { useCallback, useEffect, useMemo, useState } from 'react';
import {
    BookOpen,
    FileText,
    GitBranch,
    Lightbulb,
    MessageSquareText,
    Palette,
    Plus,
    Search,
    Trash2,
    X,
} from 'lucide-react';
import { toast } from 'sonner';

import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';

/* ─── Types ─────────────────────────────────────────── */

type EntryType = 'term' | 'decision' | 'constraint' | 'user-feedback' | 'design-rule';

interface KnowledgeEntry {
    id: string;
    type: EntryType;
    title: string;
    content: string;
    tags: string[];
    source?: string;
    createdAt: number;
    updatedAt: number;
}

/* ─── Constants ─────────────────────────────────────── */

const TYPE_CONFIG: Record<EntryType, { label: string; icon: React.ComponentType<{ size?: number }>; color: string }> = {
    term: { label: '术语', icon: BookOpen, color: '#1677ff' },
    decision: { label: '设计决策', icon: GitBranch, color: '#722ed1' },
    constraint: { label: '约束条件', icon: Lightbulb, color: '#fa8c16' },
    'user-feedback': { label: '用户反馈', icon: MessageSquareText, color: '#52c41a' },
    'design-rule': { label: '设计规则', icon: Palette, color: '#eb2f96' },
};

/* ─── Component ─────────────────────────────────────── */

interface KnowledgeBasePanelProps {
    visible: boolean;
    onClose: () => void;
    serverUrl?: string;
}

export default function KnowledgeBasePanel({ visible, onClose, serverUrl }: KnowledgeBasePanelProps) {
    const [entries, setEntries] = useState<KnowledgeEntry[]>([]);
    const [loading, setLoading] = useState(false);
    const [searchQuery, setSearchQuery] = useState('');
    const [typeFilter, setTypeFilter] = useState<EntryType | 'all'>('all');
    const [showCreateDialog, setShowCreateDialog] = useState(false);
    const [editingEntry, setEditingEntry] = useState<KnowledgeEntry | null>(null);
    const [expandedId, setExpandedId] = useState<string | null>(null);

    // 表单状态
    const [formType, setFormType] = useState<EntryType>('decision');
    const [formTitle, setFormTitle] = useState('');
    const [formContent, setFormContent] = useState('');
    const [formTags, setFormTags] = useState('');
    const [formSource, setFormSource] = useState('');
    const [saving, setSaving] = useState(false);

    const baseUrl = serverUrl || '';

    /** 加载条目 */
    const loadEntries = useCallback(async () => {
        setLoading(true);
        try {
            const params = new URLSearchParams();
            if (searchQuery.trim()) params.set('q', searchQuery.trim());
            if (typeFilter !== 'all') params.set('type', typeFilter);
            const url = `${baseUrl}/api/knowledge-base?${params.toString()}`;
            const response = await fetch(url);
            const data = await response.json();
            if (data.ok) {
                setEntries(data.entries ?? []);
            }
        } catch (err) {
            console.error('Failed to load knowledge base:', err);
        } finally {
            setLoading(false);
        }
    }, [baseUrl, searchQuery, typeFilter]);

    useEffect(() => {
        if (visible) void loadEntries();
    }, [visible, loadEntries]);

    /** 保存条目（创建或更新） */
    const handleSave = useCallback(async () => {
        if (!formTitle.trim() || !formContent.trim()) {
            toast.error('标题和内容不能为空');
            return;
        }
        setSaving(true);
        try {
            const body = {
                type: formType,
                title: formTitle.trim(),
                content: formContent.trim(),
                tags: formTags.split(',').map((t) => t.trim()).filter(Boolean),
                source: formSource.trim() || undefined,
            };

            const url = editingEntry
                ? `${baseUrl}/api/knowledge-base/entries/${editingEntry.id}`
                : `${baseUrl}/api/knowledge-base/entries`;
            const method = editingEntry ? 'PUT' : 'POST';

            const response = await fetch(url, {
                method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body),
            });
            const data = await response.json();
            if (data.ok) {
                toast.success(editingEntry ? '已更新' : '已创建');
                setShowCreateDialog(false);
                setEditingEntry(null);
                resetForm();
                void loadEntries();
            } else {
                toast.error(data.error || '保存失败');
            }
        } catch (err) {
            toast.error('保存失败: ' + String(err));
        } finally {
            setSaving(false);
        }
    }, [formType, formTitle, formContent, formTags, formSource, editingEntry, baseUrl, loadEntries]);

    /** 删除条目 */
    const handleDelete = useCallback(async (entry: KnowledgeEntry) => {
        if (!confirm(`确定删除「${entry.title}」？`)) return;
        try {
            const response = await fetch(`${baseUrl}/api/knowledge-base/entries/${entry.id}`, {
                method: 'DELETE',
            });
            const data = await response.json();
            if (data.ok) {
                toast.success('已删除');
                void loadEntries();
            } else {
                toast.error(data.error || '删除失败');
            }
        } catch (err) {
            toast.error('删除失败: ' + String(err));
        }
    }, [baseUrl, loadEntries]);

    /** 打开编辑对话框 */
    const openEdit = useCallback((entry: KnowledgeEntry) => {
        setEditingEntry(entry);
        setFormType(entry.type);
        setFormTitle(entry.title);
        setFormContent(entry.content);
        setFormTags((entry.tags ?? []).join(', '));
        setFormSource(entry.source ?? '');
        setShowCreateDialog(true);
    }, []);

    /** 重置表单 */
    const resetForm = useCallback(() => {
        setFormType('decision');
        setFormTitle('');
        setFormContent('');
        setFormTags('');
        setFormSource('');
    }, []);

    /** 打开创建对话框 */
    const openCreate = useCallback(() => {
        setEditingEntry(null);
        resetForm();
        setShowCreateDialog(true);
    }, [resetForm]);

    /** 过滤后的条目 */
    const filteredEntries = useMemo(() => {
        let result = entries;
        if (searchQuery.trim()) {
            const q = searchQuery.toLowerCase();
            result = result.filter((e) =>
                e.title.toLowerCase().includes(q) || e.content.toLowerCase().includes(q),
            );
        }
        if (typeFilter !== 'all') {
            result = result.filter((e) => e.type === typeFilter);
        }
        return result;
    }, [entries, searchQuery, typeFilter]);

    /** 格式化时间 */
    const fmtTime = (ts: number) => {
        const d = new Date(ts);
        return `${d.getFullYear()}/${(d.getMonth() + 1).toString().padStart(2, '0')}/${d.getDate().toString().padStart(2, '0')}`;
    };

    if (!visible) return null;

    const TypeIconComponent = ({ type, size }: { type: EntryType; size?: number }) => {
        const Icon = TYPE_CONFIG[type]?.icon || FileText;
        return <Icon size={size ?? 14} />;
    };

    return (
        <div className="fixed inset-0 z-50 flex items-start justify-center bg-black/30 pt-8">
            <div className="w-full max-w-2xl rounded-lg border border-border bg-background shadow-xl">
                {/* ─── Header ─── */}
                <div className="flex items-center justify-between border-b border-border px-4 py-3">
                    <div className="flex items-center gap-2 text-sm font-medium">
                        <BookOpen size={16} />
                        产品知识库
                        <span className="text-xs text-muted-foreground">({entries.length} 条)</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <Button variant="outline" size="sm" className="h-7 gap-1 text-xs" onClick={openCreate}>
                            <Plus size={13} /> 新增
                        </Button>
                        <Button variant="ghost" size="icon" className="h-7 w-7" onClick={onClose}>
                            <X size={14} />
                        </Button>
                    </div>
                </div>

                {/* ─── Search & Filter ─── */}
                <div className="flex items-center gap-2 border-b border-border/50 px-4 py-2">
                    <div className="relative flex-1">
                        <Search size={13} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-muted-foreground" />
                        <Input
                            className="h-8 pl-8 text-xs"
                            placeholder="搜索知识库..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                        />
                    </div>
                    <Select
                        value={typeFilter}
                        onValueChange={(v) => setTypeFilter(v as EntryType | 'all')}
                    >
                        <SelectTrigger className="h-8 w-[120px] text-xs">
                            <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="all" className="text-xs">全部类型</SelectItem>
                            {Object.entries(TYPE_CONFIG).map(([key, cfg]) => (
                                <SelectItem key={key} value={key} className="text-xs">
                                    {cfg.label}
                                </SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                </div>

                {/* ─── Body ─── */}
                <div className="max-h-[60vh] overflow-y-auto p-4">
                    {loading ? (
                        <div className="py-12 text-center text-xs text-muted-foreground">加载中...</div>
                    ) : filteredEntries.length === 0 ? (
                        <div className="flex flex-col items-center gap-2 py-12 text-xs text-muted-foreground">
                            <BookOpen size={24} />
                            <span>知识库为空</span>
                            <span>AI 会在标注和评审过程中自动提取知识条目</span>
                            <Button variant="outline" size="sm" className="mt-2" onClick={openCreate}>
                                手动添加第一条
                            </Button>
                        </div>
                    ) : (
                        <div className="space-y-2">
                            {filteredEntries.map((entry) => (
                                <div
                                    key={entry.id}
                                    className="group rounded-md border border-border/50 px-3 py-2 hover:border-border transition-colors"
                                >
                                    <div className="flex items-start gap-2">
                                        <span
                                            className="mt-0.5 shrink-0"
                                            style={{ color: TYPE_CONFIG[entry.type]?.color }}
                                        >
                                            <TypeIconComponent type={entry.type} />
                                        </span>
                                        <div
                                            className="flex-1 min-w-0 cursor-pointer"
                                            onClick={() => setExpandedId(expandedId === entry.id ? null : entry.id)}
                                        >
                                            <div className="flex items-center gap-2">
                                                <span
                                                    className="rounded px-1.5 py-0.5 text-[10px] font-medium"
                                                    style={{
                                                        backgroundColor: TYPE_CONFIG[entry.type]?.color + '18',
                                                        color: TYPE_CONFIG[entry.type]?.color,
                                                    }}
                                                >
                                                    {TYPE_CONFIG[entry.type]?.label ?? entry.type}
                                                </span>
                                                <span className="text-xs font-medium truncate">{entry.title}</span>
                                                <span className="ml-auto text-[10px] text-muted-foreground shrink-0">
                                                    {fmtTime(entry.updatedAt)}
                                                </span>
                                            </div>
                                            {expandedId === entry.id && (
                                                <div className="mt-2 space-y-2">
                                                    <p className="text-xs text-foreground/80 whitespace-pre-wrap">
                                                        {entry.content}
                                                    </p>
                                                    {entry.tags && entry.tags.length > 0 && (
                                                        <div className="flex flex-wrap gap-1">
                                                            {entry.tags.map((tag) => (
                                                                <span
                                                                    key={tag}
                                                                    className="rounded bg-muted px-1.5 py-0.5 text-[10px] text-muted-foreground"
                                                                >
                                                                    {tag}
                                                                </span>
                                                            ))}
                                                        </div>
                                                    )}
                                                    {entry.source && (
                                                        <p className="text-[10px] text-muted-foreground">
                                                            来源: {entry.source}
                                                        </p>
                                                    )}
                                                </div>
                                            )}
                                        </div>
                                        <div className="flex shrink-0 items-center gap-0.5 opacity-0 group-hover:opacity-100">
                                            <TooltipProvider>
                                                <Tooltip>
                                                    <TooltipTrigger asChild>
                                                        <Button
                                                            variant="ghost"
                                                            size="icon"
                                                            className="h-6 w-6"
                                                            onClick={() => openEdit(entry)}
                                                        >
                                                            <FileText size={11} />
                                                        </Button>
                                                    </TooltipTrigger>
                                                    <TooltipContent>编辑</TooltipContent>
                                                </Tooltip>
                                            </TooltipProvider>
                                            <TooltipProvider>
                                                <Tooltip>
                                                    <TooltipTrigger asChild>
                                                        <Button
                                                            variant="ghost"
                                                            size="icon"
                                                            className="h-6 w-6 text-red-400 hover:text-red-500"
                                                            onClick={() => handleDelete(entry)}
                                                        >
                                                            <Trash2 size={11} />
                                                        </Button>
                                                    </TooltipTrigger>
                                                    <TooltipContent>删除</TooltipContent>
                                                </Tooltip>
                                            </TooltipProvider>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                {/* ─── Footer ─── */}
                <div className="border-t border-border px-4 py-2">
                    <p className="text-[10px] text-muted-foreground">
                        显示 {filteredEntries.length} / {entries.length} 条
                    </p>
                </div>
            </div>

            {/* ─── 创建/编辑对话框 ─── */}
            <Dialog open={showCreateDialog} onOpenChange={(open) => { if (!open) { setShowCreateDialog(false); setEditingEntry(null); } }}>
                <DialogContent className="sm:max-w-lg">
                    <DialogHeader>
                        <DialogTitle className="text-sm">
                            {editingEntry ? '编辑知识条目' : '新增知识条目'}
                        </DialogTitle>
                    </DialogHeader>
                    <div className="space-y-3 py-2">
                        <div className="grid grid-cols-2 gap-3">
                            <div className="space-y-1.5">
                                <label className="text-xs text-muted-foreground">类型</label>
                                <Select value={formType} onValueChange={(v) => setFormType(v as EntryType)}>
                                    <SelectTrigger className="h-8 text-xs">
                                        <SelectValue />
                                    </SelectTrigger>
                                    <SelectContent>
                                        {Object.entries(TYPE_CONFIG).map(([key, cfg]) => (
                                            <SelectItem key={key} value={key} className="text-xs">
                                                {cfg.label}
                                            </SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>
                            </div>
                            <div className="space-y-1.5">
                                <label className="text-xs text-muted-foreground">标签（逗号分隔）</label>
                                <Input
                                    className="h-8 text-xs"
                                    placeholder="如: 首页, 登录"
                                    value={formTags}
                                    onChange={(e) => setFormTags(e.target.value)}
                                />
                            </div>
                        </div>
                        <div className="space-y-1.5">
                            <label className="text-xs text-muted-foreground">标题 *</label>
                            <Input
                                className="h-8 text-xs"
                                placeholder="知识条目标题"
                                value={formTitle}
                                onChange={(e) => setFormTitle(e.target.value)}
                            />
                        </div>
                        <div className="space-y-1.5">
                            <label className="text-xs text-muted-foreground">内容 *</label>
                            <Textarea
                                className="min-h-[100px] text-xs"
                                placeholder="详细描述（支持 Markdown）"
                                value={formContent}
                                onChange={(e) => setFormContent(e.target.value)}
                            />
                        </div>
                        <div className="space-y-1.5">
                            <label className="text-xs text-muted-foreground">来源（可选）</label>
                            <Input
                                className="h-8 text-xs"
                                placeholder="如: prototype:home, chat:xxx"
                                value={formSource}
                                onChange={(e) => setFormSource(e.target.value)}
                            />
                        </div>
                    </div>
                    <DialogFooter>
                        <Button variant="outline" size="sm" onClick={() => { setShowCreateDialog(false); setEditingEntry(null); }}>
                            取消
                        </Button>
                        <Button size="sm" onClick={handleSave} disabled={!formTitle.trim() || !formContent.trim() || saving}>
                            {saving ? '保存中...' : editingEntry ? '更新' : '创建'}
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </div>
    );
}
