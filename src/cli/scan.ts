/**
 * `make scan` 命令 — 扫描前端项目并导入到 Axhub Make
 */

import path from 'node:path';
import { scanProject } from './detectors/framework-detector.ts';
import { writeClientJson, writeSidebarTree } from './generators/make-json-generator.ts';

export const SCAN_USAGE = `Usage: axhub-make scan [project-dir] [options]

Scan a frontend project and import it into Axhub Make.

Options:
  --framework <type>       Force framework detection (react|vue|auto).
                           Default: auto-detect from package.json.
  --entry <path>           Entry directory relative to project root.
                           Default: src/
  --out-dir <path>         Output directory for .axhub/make/ files.
                           Default: project root.
  --init                   Also initialize client.json if missing.
  --enable                 Enable annotation for discovered pages.
  --server-url <url>       Axhub Make server URL (e.g. http://localhost:7600).
  -h, --help               Show this help message.

Examples:
  axhub-make scan                           # Scan current directory
  axhub-make scan ../my-app                 # Scan specific project
  axhub-make scan --framework vue           # Force Vue detection
  axhub-make scan --init                    # Also create client.json
  axhub-make scan --enable --server-url http://localhost:7600  # Scan and enable annotations
`;

interface ScanCommandOptions {
  projectDir: string;
  framework?: 'react' | 'vue' | 'auto';
  entry?: string;
  outDir?: string;
  init?: boolean;
  help?: boolean;
  enable?: boolean;
  serverUrl?: string;
}

export function parseScanArgs(args: string[], cwd = process.cwd()): ScanCommandOptions {
  const options: ScanCommandOptions = {
    projectDir: cwd,
    framework: 'auto',
  };

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];

    if (arg === '--help' || arg === '-h') {
      options.help = true;
      continue;
    }
    if (arg === '--framework') {
      const value = args[++i];
      if (value !== 'react' && value !== 'vue' && value !== 'auto') {
        throw new Error(`Invalid --framework: ${value}. Use react, vue, or auto.`);
      }
      options.framework = value;
      continue;
    }
    if (arg === '--entry') {
      options.entry = args[++i];
      continue;
    }
    if (arg === '--out-dir') {
      options.outDir = path.resolve(cwd, args[++i]);
      continue;
    }
    if (arg === '--init') {
      options.init = true;
      continue;
    }
    if (arg === '--enable') {
      options.enable = true;
      continue;
    }
    if (arg === '--server-url') {
      options.serverUrl = args[++i];
      continue;
    }
    // 第一个非选项参数作为项目目录
    if (!arg.startsWith('--')) {
      options.projectDir = path.resolve(cwd, arg);
      continue;
    }
  }

  return options;
}

export async function runScanCommand(args: string[], cwd = process.cwd()): Promise<void> {
  const options = parseScanArgs(args, cwd);

  if (options.help) {
    console.log(SCAN_USAGE.trimEnd());
    return;
  }

  const projectDir = options.projectDir;
  const outDir = options.outDir || projectDir;

  // 如果指定了 --server-url，后续用于调用 API
  const serverUrl = options.serverUrl || '';

  console.log(`\n🔍 正在扫描项目: ${projectDir}`);

  // 执行扫描
  const scanResult = scanProject(projectDir);

  // 框架检测结果
  const frameworkLabel: Record<string, string> = {
    react: 'React',
    vue: 'Vue',
    unknown: '未能识别',
  };
  console.log(`  框架: ${frameworkLabel[scanResult.framework] ?? '未知'} (置信度: ${Math.round(scanResult.confidence * 100)}%)`);

  // 强制框架类型
  if (options.framework && options.framework !== 'auto' && scanResult.framework === 'unknown') {
    scanResult.framework = options.framework;
    console.log(`  已强制指定框架: ${frameworkLabel[options.framework]}`);
  }

  // 页面发现结果
  if (scanResult.pages.length > 0) {
    console.log(`\n📄 发现 ${scanResult.pages.length} 个页面:`);
    for (const page of scanResult.pages) {
      console.log(`   - ${page}`);
    }
  } else {
    console.log('\n⚠️  未发现可识别的页面文件');
    console.log('   你可以手动创建原型页面，或使用 --entry 指定入口目录');
    return;
  }

  // 生成 .axhub/make/ 文件
  console.log(`\n📝 生成项目配置...`);

  const shouldInit = options.init || !scanResult.packageJsonPath;

  if (shouldInit) {
    const clientJson = writeClientJson(outDir);
    console.log(`   ✅ .axhub/make/client.json — 项目 ID: ${clientJson.project.id}`);
  } else {
    console.log(`   ⏭️  跳过 client.json（使用 --init 可强制生成）`);
  }

  const sidebarTree = writeSidebarTree(outDir, scanResult);
  const pageCount = sidebarTree.reduce((sum, node) => sum + (node.children?.length ?? 0), 0);
  console.log(`   ✅ .axhub/make/sidebar-tree.json — ${pageCount} 个页面`);

  console.log(`\n🎉 扫描完成！`);
  console.log(`   输出目录: ${outDir}\\.axhub\\make\\`);
  if (pageCount > 0) {
    if (options.enable && serverUrl) {
      console.log(`\n🔌 正在为 ${pageCount} 个页面启用标注...`);
      for (const node of sidebarTree) {
        for (const child of node.children ?? []) {
          try {
            const url = `${serverUrl}/api/prototype-annotation/enable`;
            const response = await fetch(url, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ targetPath: `prototypes/${child.id}` }),
            });
            const data = await response.json();
            if (data.ok) {
              console.log(`   ✅ ${child.label}: 标注已启用${data.changedIndex ? '（已注入 AnnotationViewer）' : ''}`);
            } else {
              console.log(`   ❌ ${child.label}: ${data.error || '启用失败'}`);
            }
          } catch (err) {
            console.log(`   ❌ ${child.label}: 连接失败 - ${err}`);
          }
        }
      }
    } else if (options.enable && !serverUrl) {
      console.log('\n⚠️  跳过启用标注：未指定 --server-url');
      console.log('   示例: axhub-make scan --enable --server-url http://localhost:7600');
    }

    console.log(`\n下一步:`);
    console.log(`   1. 在项目中启动 Axhub Make: axhub-make --project-root "${outDir}"`);
    console.log(`   2. 或在管理界面中导入现有原型`);
  }
}
