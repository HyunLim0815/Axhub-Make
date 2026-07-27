/**
 * Framework detector — 自动检测项目使用的框架类型
 */

import fs from 'node:fs';
import path from 'node:path';

export type FrameworkType = 'react' | 'vue' | 'unknown';

export interface ScanResult {
  framework: FrameworkType;
  /** 项目根目录下的 package.json（如果存在） */
  packageJsonPath: string | null;
  /** 检测到的页面入口文件路径 */
  pages: string[];
  /** 框架置信度（0-1） */
  confidence: number;
}

/** 检测指定目录的项目框架 */
export function detectFramework(projectDir: string): FrameworkType {
  const pkgPath = path.join(projectDir, 'package.json');
  if (!fs.existsSync(pkgPath)) return 'unknown';

  try {
    const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));
    const deps = { ...pkg.dependencies, ...pkg.devDependencies };
    if (deps.react) return 'react';
    if (deps.vue || deps['vue-router']) return 'vue';
  } catch {
    // ignore parse errors
  }
  return 'unknown';
}

/** 扫描项目中的页面入口文件 */
export function scanPages(projectDir: string, framework: FrameworkType): string[] {
  const pages: string[] = [];
  const srcDir = path.join(projectDir, 'src');

  if (!fs.existsSync(srcDir)) return pages;

  const scanDir = (dir: string, depth: number) => {
    if (depth > 4) return; // 限制扫描深度
    let entries: string[];
    try {
      entries = fs.readdirSync(dir, { withFileTypes: true });
    } catch {
      return;
    }

    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        // 跳过 node_modules, .git, .axhub 等
        if (entry.name.startsWith('.') || entry.name === 'node_modules' || entry.name === 'dist') continue;
        scanDir(fullPath, depth + 1);
      } else if (entry.isFile()) {
        const relative = path.relative(projectDir, fullPath).replace(/\\/g, '/');

        if (framework === 'react' && (entry.name === 'index.tsx' || entry.name === 'index.jsx' || entry.name === 'main.tsx' || entry.name === 'main.jsx')) {
          // 只在 src/pages/ 或 src/ 一级目录下检测
          const parentDir = path.basename(path.dirname(fullPath));
          if (parentDir === 'src' || parentDir === 'pages' || depth <= 2) {
            pages.push(relative);
          }
        } else if (framework === 'vue' && (entry.name.endsWith('.vue') && entry.name !== 'App.vue')) {
          pages.push(relative);
        }
      }
    }
  };

  scanDir(srcDir, 0);

  // 如果没找到页面文件，加入 src 目录作为默认入口
  if (pages.length === 0) {
    const indexFiles = ['index.tsx', 'index.jsx', 'index.ts', 'index.js', 'main.ts', 'main.js'];
    for (const idx of indexFiles) {
      const idxPath = path.join(srcDir, idx);
      if (fs.existsSync(idxPath)) {
        pages.push(`src/${idx}`);
        break;
      }
    }
  }

  return pages;
}

/** 完整的项目扫描 */
export function scanProject(projectDir: string): ScanResult {
  const framework = detectFramework(projectDir);
  const pages = scanPages(projectDir, framework);
  const pkgPath = path.join(projectDir, 'package.json');
  const packageJsonPath = fs.existsSync(pkgPath) ? pkgPath : null;

  const confidence = framework === 'unknown' ? 0.3 : pages.length > 0 ? 0.9 : 0.5;

  return { framework, packageJsonPath, pages, confidence };
}
