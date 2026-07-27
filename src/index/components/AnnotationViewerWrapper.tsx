/**
 * AnnotationViewerWrapper — 增强版标注查看器
 *
 * 在 @axhub/annotation 的 AnnotationViewer 基础上，增加
 * 页面级标注（scope: 'page'）的展示支持。
 *
 * 使用方法：替换原有的 <AnnotationViewer> 引用
 *
 * ```tsx
 * import AnnotationViewerWrapper from './AnnotationViewerWrapper';
 * <AnnotationViewerWrapper source={source} options={options} />
 * ```
 */

import React, { useCallback, useMemo, useState } from 'react';
import {
    AnnotationViewer,
    type AnnotationSourceDocument,
    type AnnotationViewerOptions,
} from '@axhub/annotation';

/* ─── Types ─────────────────────────────────────────── */

interface AugmentedAnnotationNode {
    id: string;
    title?: string;
    scope?: 'element' | 'page';
    pageId?: string | string[];
    hasMarkdown?: boolean;
    color?: string;
    [key: string]: unknown;
}

interface AugmentedSourceData {
    version: number;
    prototypeName?: string;
    pageId?: string;
    nodes: AugmentedAnnotationNode[];
    updatedAt?: number;
    [key: string]: unknown;
}

interface AugmentedSourceDocument extends Omit<AnnotationSourceDocument, 'data'> {
    data: AugmentedSourceData;
}

/* ─── Component ─────────────────────────────────────── */

interface AnnotationViewerWrapperProps {
    source: AugmentedSourceDocument | (() => AugmentedSourceDocument);
    options?: AnnotationViewerOptions;
    /** 是否显示页面级标注标签页（默认 true） */
    showPageAnnotations?: boolean;
}

export default function AnnotationViewerWrapper({
    source,
    options,
    showPageAnnotations = true,
}: AnnotationViewerWrapperProps) {
    const [activeTab, setActiveTab] = useState<'all' | 'element' | 'page'>('all');

    /** 解析 source */
    const resolvedSource = useMemo(() => {
        const src = typeof source === 'function' ? source() : source;
        return src as AugmentedSourceDocument;
    }, [source]);

    /** 分离页面级和元素级标注 */
    const { pageAnnotations, elementAnnotations } = useMemo(() => {
        const nodes = resolvedSource.data?.nodes ?? [];
        return {
            pageAnnotations: nodes.filter((n) => n.scope === 'page'),
            elementAnnotations: nodes.filter((n) => !n.scope || n.scope === 'element'),
        };
    }, [resolvedSource]);

    /** 过滤后的 source（传给原生 AnnotationViewer） */
    const filteredSource = useMemo(() => {
        if (activeTab === 'page') {
            // 页面标注模式：清空 nodes 让原生 viewer 不显示元素徽章
            return {
                ...resolvedSource,
                data: {
                    ...resolvedSource.data,
                    nodes: [],
                },
            } as AnnotationSourceDocument;
        }
        if (activeTab === 'element') {
            return {
                ...resolvedSource,
                data: {
                    ...resolvedSource.data,
                    nodes: elementAnnotations,
                },
            } as AnnotationSourceDocument;
        }
        // 'all': 保留全部
        return resolvedSource as unknown as AnnotationSourceDocument;
    }, [resolvedSource, activeTab, elementAnnotations]);

    /** 获取当前页的页面级标注 */
    const getCurrentPageAnnotations = useCallback(() => {
        const currentPage = options?.currentPageId;
        if (!currentPage) return pageAnnotations;
        return pageAnnotations.filter((n) => {
            const pageIds = Array.isArray(n.pageId) ? n.pageId : [n.pageId];
            return pageIds.includes(currentPage);
        });
    }, [pageAnnotations, options?.currentPageId]);

    const currentPageAnnotations = getCurrentPageAnnotations();

    return (
        <div className="axhub-annotation-wrapper" style={{ position: 'relative', width: '100%', height: '100%' }}>
            {/* 原生标注查看器（处理元素级标注） */}
            {activeTab !== 'page' && (
                <AnnotationViewer
                    source={filteredSource}
                    options={options}
                />
            )}

            {/* 页面级标注切换标签 */}
            {showPageAnnotations && pageAnnotations.length > 0 && (
                <div style={{
                    position: 'absolute',
                    top: 8,
                    right: 8,
                    zIndex: 100,
                    display: 'flex',
                    gap: 4,
                    background: 'rgba(255,255,255,0.95)',
                    borderRadius: 8,
                    padding: 4,
                    boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                    fontSize: 12,
                }}>
                    {(['all', 'element', 'page'] as const).map((tab) => {
                        const counts: Record<string, number> = {
                            all: resolvedSource.data?.nodes?.length ?? 0,
                            element: elementAnnotations.length,
                            page: pageAnnotations.length,
                        };
                        return (
                            <button
                                key={tab}
                                onClick={() => setActiveTab(tab)}
                                style={{
                                    padding: '4px 10px',
                                    border: 'none',
                                    borderRadius: 6,
                                    cursor: 'pointer',
                                    fontWeight: activeTab === tab ? 600 : 400,
                                    background: activeTab === tab ? '#1677ff' : 'transparent',
                                    color: activeTab === tab ? '#fff' : '#666',
                                    transition: 'all 0.15s',
                                }}
                            >
                                {tab === 'all' ? '全部' : tab === 'element' ? '元素' : '页面'}
                                {' '}
                                <span style={{ opacity: 0.7, fontSize: 10 }}>{counts[tab]}</span>
                            </button>
                        );
                    })}
                </div>
            )}

            {/* 页面级标注列表 */}
            {activeTab !== 'element' && currentPageAnnotations.length > 0 && (
                <div style={{
                    position: 'absolute',
                    bottom: 8,
                    left: 8,
                    right: 8,
                    zIndex: 100,
                    display: 'flex',
                    flexDirection: 'column',
                    gap: 4,
                    maxHeight: '40%',
                    overflowY: 'auto',
                }}>
                    {currentPageAnnotations.map((ann) => (
                        <div
                            key={ann.id}
                            style={{
                                background: 'rgba(255,255,255,0.95)',
                                borderRadius: 8,
                                padding: '8px 12px',
                                boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
                                borderLeft: `3px solid ${ann.color ?? '#1677ff'}`,
                                fontSize: 13,
                            }}
                        >
                            <div style={{ fontWeight: 600, marginBottom: 2 }}>
                                {ann.title || '页面标注'}
                            </div>
                            {ann.hasMarkdown && ann.id && resolvedSource.markdownMap?.[ann.id] && (
                                <div style={{ color: '#555', fontSize: 12, lineHeight: 1.5, whiteSpace: 'pre-wrap' }}>
                                    {resolvedSource.markdownMap[ann.id]}
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
