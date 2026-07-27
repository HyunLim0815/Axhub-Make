/**
 * Knowledge context provider — 将知识库内容注入到 AI Prompt 中
 *
 * 提供格式化后的知识库上下文文本，供原型生成、标注生成等 AI 流程使用。
 */

import { getAllEntries, searchEntries, type KnowledgeEntry, type KnowledgeEntryType } from './knowledge-store.ts';

/** 将知识条目格式化为上下文文本 */
export function formatEntryAsContext(entry: KnowledgeEntry): string {
  const typeLabels: Record<string, string> = {
    term: '📖 术语',
    decision: '🎯 设计决策',
    constraint: '⚠️ 约束条件',
    'user-feedback': '💬 用户反馈',
    'design-rule': '🎨 设计规则',
  };

  const label = typeLabels[entry.type] ?? entry.type;
  const tags = entry.tags.length > 0 ? ` [${entry.tags.join(', ')}]` : '';
  return `- **${label}${tags}**: ${entry.title} — ${entry.content.slice(0, 200)}`;
}

/** 格式化知识库为 AI Prompt 上下文块 */
export function formatKnowledgeContext(
  entries: KnowledgeEntry[],
  maxEntries = 20,
): string {
  if (entries.length === 0) return '';

  const selected = entries.slice(0, maxEntries);
  const context = selected.map(formatEntryAsContext).join('\n');

  return [
    '## 项目知识库上下文',
    '',
    '以下是该项目已有的产品知识，请在设计时参考：',
    '',
    context,
    '',
    `（共 ${entries.length} 条知识，显示前 ${selected.length} 条）`,
  ].join('\n');
}

/** 获取格式化后的知识库上下文 */
export function getKnowledgeContext(
  projectRoot: string,
  projectId: string,
  options?: {
    /** 按类型过滤 */
    type?: KnowledgeEntryType;
    /** 按关键词搜索 */
    query?: string;
    /** 最大条目数 */
    maxEntries?: number;
  },
): string {
  let entries: KnowledgeEntry[];

  if (options?.query) {
    entries = searchEntries(projectRoot, projectId, options.query);
  } else if (options?.type) {
    entries = getAllEntries(projectRoot, projectId).filter((e) => e.type === options.type);
  } else {
    entries = getAllEntries(projectRoot, projectId);
  }

  return formatKnowledgeContext(entries, options?.maxEntries ?? 20);
}

/** 获取与原型生成相关的知识上下文（术语 + 设计规则 + 约束优先） */
export function getPrototypeGenerationContext(
  projectRoot: string,
  projectId: string,
  prototypeName?: string,
): string {
  // 先搜索与原型名称相关的条目
  let entries: KnowledgeEntry[] = [];
  if (prototypeName) {
    entries = searchEntries(projectRoot, projectId, prototypeName);
  }

  // 补充关键类型（术语、设计规则、约束）
  const priorityTypes: KnowledgeEntryType[] = ['term', 'design-rule', 'constraint'];
  const allEntries = getAllEntries(projectRoot, projectId);

  for (const type of priorityTypes) {
    const typeEntries = allEntries.filter((e) => e.type === type && !entries.some((ex) => ex.id === e.id));
    entries = [...entries, ...typeEntries];
  }

  if (entries.length === 0) return '';

  return [
    '## 项目知识库上下文',
    '',
    '以下是与当前原型相关的项目知识。请在设计时遵循已有的术语定义、设计规则和约束条件：',
    '',
    ...entries.map(formatEntryAsContext),
    '',
    '请在原型中保持与上述知识的一致性。',
  ].join('\n');
}
