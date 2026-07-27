/**
 * client.json 和 sidebar-tree.json 生成器
 */

import fs from 'node:fs';
import path from 'node:path';
import type { ScanResult } from '../detectors/framework-detector.ts';

interface ClientJson {
  schemaVersion: number;
  kind: 'axhub-make-client';
  repository: string;
  project: {
    id: string;
    name: string;
  };
}

interface SidebarTreeNode {
  id: string;
  label: string;
  type: 'folder' | 'prototype' | 'doc';
  children?: SidebarTreeNode[];
}

/** 从项目名生成一个稳定的 project ID */
function generateProjectId(projectName: string): string {
  return projectName
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 64) || 'untitled-project';
}

/** 获取项目名称 */
function getProjectName(projectDir: string): string {
  const pkgPath = path.join(projectDir, 'package.json');
  try {
    const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));
    if (pkg.name) return pkg.name;
  } catch {
    // ignore
  }
  return path.basename(projectDir);
}

/** 生成 client.json */
export function generateClientJson(projectDir: string): ClientJson {
  const projectName = getProjectName(projectDir);
  return {
    schemaVersion: 1,
    kind: 'axhub-make-client',
    repository: '',
    project: {
      id: generateProjectId(projectName),
      name: projectName,
    },
  };
}

/** 将扫描到的页面转换为侧边栏树节点 */
export function generateSidebarTree(scanResult: ScanResult): SidebarTreeNode[] {
  const nodes: SidebarTreeNode[] = [];

  if (scanResult.pages.length > 0) {
    const pagesNode: SidebarTreeNode = {
      id: 'prototypes',
      label: '原型页面',
      type: 'folder',
      children: scanResult.pages.map((page, index) => ({
        id: `page-${index + 1}`,
        label: page.split('/').pop()?.replace(/\.(tsx|jsx|vue|ts|js)$/i, '') || `page-${index + 1}`,
        type: 'prototype' as const,
      })),
    };
    nodes.push(pagesNode);
  }

  return nodes;
}

/** 确保 .axhub/make 目录存在 */
export function ensureMakeDir(projectDir: string): string {
  const makeDir = path.join(projectDir, '.axhub', 'make');
  fs.mkdirSync(makeDir, { recursive: true });
  return makeDir;
}

/** 将 client.json 写入到 .axhub/make/client.json */
export function writeClientJson(projectDir: string): ClientJson {
  const makeDir = ensureMakeDir(projectDir);
  const clientJson = generateClientJson(projectDir);
  fs.writeFileSync(
    path.join(makeDir, 'client.json'),
    `${JSON.stringify(clientJson, null, 2)}\n`,
    'utf8',
  );
  return clientJson;
}

/** 将 sidebar-tree.json 写入到 .axhub/make/sidebar-tree.json */
export function writeSidebarTree(projectDir: string, scanResult: ScanResult): SidebarTreeNode[] {
  const makeDir = ensureMakeDir(projectDir);
  const tree = generateSidebarTree(scanResult);
  fs.writeFileSync(
    path.join(makeDir, 'sidebar-tree.json'),
    `${JSON.stringify(tree, null, 2)}\n`,
    'utf8',
  );
  return tree;
}
