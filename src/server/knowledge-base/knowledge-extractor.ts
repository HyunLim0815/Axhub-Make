/**
 * AI 知识抽取管道
 *
 * 在标注创建/更新、评审完成、对话结束时自动从内容中抽取
 * 产品术语、设计决策、约束条件等知识条目。
 */

import type { KnowledgeEntryType } from './knowledge-store.ts';
import { createEntry, searchEntries } from './knowledge-store.ts';

/* ─── 抽取配置 ─────────────────────────────────────── */

interface ExtractionRule {
  type: KnowledgeEntryType;
  /**
   * 从文本中检测该类型知识的触发模式。
   * 简单的关键词匹配，用于快速判定是否需要调用 LLM。
   */
  triggerKeywords: string[];
  /**
   * LLM 抽取的 System Prompt 片段
   */
  extractionPrompt: string;
}

const EXTRACTION_RULES: ExtractionRule[] = [
  {
    type: 'term',
    triggerKeywords: ['术语', '定义', '简称', '缩写', '指的是', '称为'],
    extractionPrompt: `从以下产品对话文本中提取产品术语和定义。
每项输出 JSON 格式: { "title": "术语名称", "content": "术语定义" }
只提取明确的产品或业务术语。`,
  },
  {
    type: 'decision',
    triggerKeywords: ['决定', '决策', '选择', '采用', '放弃', '确认', '同意'],
    extractionPrompt: `从以下产品对话文本中提取设计决策。
每项输出 JSON 格式: { "title": "决策标题", "content": "决策详情（含原因和替代方案）" }
只提取有明确结论的设计或产品决策。`,
  },
  {
    type: 'constraint',
    triggerKeywords: ['限制', '约束', '必须', '不能', '不支持', '仅', '只支持'],
    extractionPrompt: `从以下产品对话文本中提取约束条件。
每项输出 JSON 格式: { "title": "约束标题", "content": "约束详情" }
只提取技术或业务上的硬性约束。`,
  },
  {
    type: 'user-feedback',
    triggerKeywords: ['反馈', '建议', '意见', '问题', '体验', '不好', '改进'],
    extractionPrompt: `从以下产品对话文本中提取用户反馈。
每项输出 JSON 格式: { "title": "反馈主题", "content": "反馈详情" }
只提取有价值的、具体的用户反馈。`,
  },
  {
    type: 'design-rule',
    triggerKeywords: ['设计规范', '风格', '颜色', '间距', '字体', '对齐', '布局'],
    extractionPrompt: `从以下产品对话文本中提取设计规则。
每项输出 JSON 格式: { "title": "规则名称", "content": "规则详情（含具体数值或示例）" }
只提取明确的设计规范或样式规则。`,
  },
];

/* ─── 文本分析 ──────────────────────────────────────── */

/** 检测文本是否包含可能触发知识抽取的关键词 */
export function hasTriggerKeywords(text: string): ExtractionRule[] {
  const matched: ExtractionRule[] = [];
  const lower = text.toLowerCase();
  for (const rule of EXTRACTION_RULES) {
    if (rule.triggerKeywords.some((kw) => lower.includes(kw))) {
      matched.push(rule);
    }
  }
  return matched;
}

/** 构造 LLM 抽取用的 Prompt */
export function buildExtractionPrompt(text: string, source: string): string {
  const rules = hasTriggerKeywords(text);
  if (rules.length === 0) return '';

  const systemPrompts = rules.map((r) => r.extractionPrompt).join('\n\n');

  return [
    '你是一个产品知识抽取助手。请从以下文本中提取知识条目。',
    '',
    systemPrompts,
    '',
    '如果没有任何可提取的知识，返回空数组 []。',
    '只返回 JSON 数组，不要包含其他文字。',
    '',
    `文本来源: ${source}`,
    '',
    '文本内容:',
    text,
  ].join('\n');
}

/** 解析 LLM 返回的 JSON */
export function parseExtractionResult(raw: string): Array<{ title: string; content: string }> {
  try {
    // 尝试直接从返回文本中提取 JSON 数组
    const jsonMatch = raw.match(/\[[\s\S]*\]/);
    if (jsonMatch) {
      return JSON.parse(jsonMatch[0]) as Array<{ title: string; content: string }>;
    }
    return [];
  } catch {
    return [];
  }
}

/* ─── 去重检测 ──────────────────────────────────────── */

/** 检查相似条目是否已存在（简单标题去重） */
export function isDuplicateEntry(
  projectRoot: string,
  projectId: string,
  title: string,
  threshold = 0.8,
): boolean {
  const existing = searchEntries(projectRoot, projectId, title);
  if (existing.length === 0) return false;

  const normalized = title.toLowerCase().trim();
  for (const entry of existing) {
    const entryTitle = entry.title.toLowerCase().trim();
    // 简单 Jaccard 相似度
    const words1 = new Set(normalized.split(/\s+/));
    const words2 = new Set(entryTitle.split(/\s+/));
    const intersection = new Set([...words1].filter((w) => words2.has(w)));
    const union = new Set([...words1, ...words2]);
    const similarity = intersection.size / union.size;
    if (similarity >= threshold) return true;
  }
  return false;
}

/* ─── 主抽取流程 ────────────────────────────────────── */

/** 从文本中自动抽取知识条目并保存 */
export async function extractAndSaveKnowledge(
  projectRoot: string,
  projectId: string,
  text: string,
  source: string,
  options?: {
    /** 自定义 LLM 调用函数。默认用 fetch 调用本地 LLM */
    llmCall?: (prompt: string) => Promise<string>;
    /** 是否检查重复 */
    skipDedup?: boolean;
  },
): Promise<{ created: number; skipped: number }> {
  // 1. 快速关键词预检
  const matchedRules = hasTriggerKeywords(text);
  if (matchedRules.length === 0) {
    return { created: 0, skipped: 0 };
  }

  // 2. 构建抽取 Prompt
  const prompt = buildExtractionPrompt(text, source);
  if (!prompt) return { created: 0, skipped: 0 };

  // 3. 调用 LLM
  let llmResult: string;
  if (options?.llmCall) {
    llmResult = await options.llmCall(prompt);
  } else {
    llmResult = await defaultLlmCall(prompt);
  }

  // 4. 解析结果
  const items = parseExtractionResult(llmResult);
  if (items.length === 0) return { created: 0, skipped: 0 };

  // 5. 保存条目（去重）
  let created = 0;
  let skipped = 0;
  for (const item of items) {
    if (!item.title || !item.content) continue;

    // 确定类型：取第一个匹配规则的类型
    const type = matchedRules[0]?.type ?? 'decision';

    // 去重
    if (!options?.skipDedup && isDuplicateEntry(projectRoot, projectId, item.title)) {
      skipped++;
      continue;
    }

    createEntry(projectRoot, projectId, {
      type,
      title: item.title,
      content: item.content,
      source,
    });
    created++;
  }

  return { created, skipped };
}

/* ─── 默认 LLM 调用 ──────────────────────────────────── */

/**
 * 默认的 LLM 调用函数。
 * 尝试调用本地运行的 LLM API（如 Ollama 或 Axhub Make 内置的 AI 服务）。
 * 如果不可用，返回空结果。
 */
async function defaultLlmCall(prompt: string): Promise<string> {
  // 尝试调用 Ollama（本地常用）
  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 10000);

    const response = await fetch('http://localhost:11434/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: 'llama3.2',
        prompt,
        stream: false,
      }),
      signal: controller.signal,
    });
    clearTimeout(timeout);

    if (response.ok) {
      const data = await response.json() as { response?: string };
      return data.response ?? '[]';
    }
  } catch {
    // LLM 不可用，静默失败
  }

  // 退回到基于规则的关键词抽取（简化版）
  return ruleBasedExtraction(prompt);
}

/** 基于关键词的简单抽取（不依赖 LLM 时的降级方案） */
function ruleBasedExtraction(_prompt: string): string {
  // 降级方案：返回空结果，让用户手动录入
  return '[]';
}

/** 判断本地 LLM 是否可用 */
export async function isLlmAvailable(): Promise<boolean> {
  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 3000);
    const response = await fetch('http://localhost:11434/api/tags', {
      signal: controller.signal,
    });
    clearTimeout(timeout);
    return response.ok;
  } catch {
    return false;
  }
}
