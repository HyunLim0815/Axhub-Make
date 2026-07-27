/**
 * Direct LLM Service — 直接从浏览器调用 OpenAI 兼容 API
 *
 * 绕过 ACP 服务，所有 AI 对话均可使用。
 */

const STORAGE_KEY_CONFIG = 'axhub_direct_llm_config';

export interface DirectLlmConfig {
  enabled: boolean;
  baseUrl: string;
  apiKey: string;
  model: string;
}

export function getDirectLlmConfig(): DirectLlmConfig {
  try {
    const raw = localStorage.getItem(STORAGE_KEY_CONFIG);
    if (raw) {
      const parsed = JSON.parse(raw) as Partial<DirectLlmConfig>;
      return {
        enabled: parsed.enabled ?? false,
        baseUrl: parsed.baseUrl || 'https://api.openai.com/v1',
        apiKey: parsed.apiKey || '',
        model: parsed.model || 'gpt-4o',
      };
    }
  } catch { /* ignore */ }
  return { enabled: false, baseUrl: 'https://api.openai.com/v1', apiKey: '', model: 'gpt-4o' };
}

export function saveDirectLlmConfig(config: DirectLlmConfig): void {
  localStorage.setItem(STORAGE_KEY_CONFIG, JSON.stringify(config));
}

/** 调用 OpenAI 兼容的 Chat Completions API */
export async function callDirectLlm(
  prompt: string,
  options?: {
    systemPrompt?: string;
    maxTokens?: number;
    signal?: AbortSignal;
  },
): Promise<string> {
  const config = getDirectLlmConfig();
  if (!config.enabled || !config.apiKey) {
    throw new Error('Direct LLM 未启用或未配置 API Key');
  }

  const messages: Array<{ role: string; content: string }> = [];
  if (options?.systemPrompt) {
    messages.push({ role: 'system', content: options.systemPrompt });
  }
  messages.push({ role: 'user', content: prompt });

  const response = await fetch(`${config.baseUrl.replace(/\/+$/, '')}/chat/completions`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${config.apiKey}`,
    },
    body: JSON.stringify({
      model: config.model,
      messages,
      max_tokens: options?.maxTokens ?? 4096,
      stream: false,
    }),
    signal: options?.signal,
  });

  if (!response.ok) {
    const text = await response.text().catch(() => '');
    throw new Error(`LLM API 错误 (${response.status}): ${text.slice(0, 200)}`);
  }

  const data = await response.json() as {
    choices?: Array<{ message?: { content?: string } }>;
  };

  const content = data.choices?.[0]?.message?.content;
  if (!content) {
    throw new Error('LLM 返回内容为空');
  }

  return content;
}

/**
 * 通用 AI 调用：优先使用直接 LLM，失败后执行 fallback
 * @returns true=直接 LLM 已处理 / false=需要执行 fallback
 */
export async function tryDirectLlmFirst(
  prompt: string,
  options?: { systemPrompt?: string },
): Promise<{ used: boolean; result?: string }> {
  const config = getDirectLlmConfig();
  if (config.enabled && config.apiKey) {
    try {
      const result = await callDirectLlm(prompt, options);
      return { used: true, result };
    } catch {
      // 直接 LLM 失败，回退
    }
  }
  return { used: false };
}

/** 同步设置对话框中的配置到 localStorage */
export function syncConfigFromForm(formState: {
  annotationDirectEnabled: boolean;
  annotationDirectBaseUrl: string;
  annotationDirectApiKey: string;
  annotationDirectModel: string;
}): void {
  saveDirectLlmConfig({
    enabled: formState.annotationDirectEnabled,
    baseUrl: formState.annotationDirectBaseUrl,
    apiKey: formState.annotationDirectApiKey,
    model: formState.annotationDirectModel,
  });
}
