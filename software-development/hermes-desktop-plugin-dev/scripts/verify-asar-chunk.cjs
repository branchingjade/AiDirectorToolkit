// 验证 app.asar 中指定 chunk 的完整性：提取 + node --check 提示 + 依赖链检查
// 用法: node verify-asar-chunk.cjs <app.asar路径> <chunk文件名>
// 例:   node verify-asar-chunk.cjs apps/desktop/release/win-unpacked/resources/app.asar completion-sound-BMJ5NAKZ.js
// 注意: 在 "type":"module" 的包目录里跑，本文件 .cjs 后缀避免 ESM 解析
const asar = require('@electron/asar');
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const p = process.argv[2];
const name = process.argv[3];
if (!p || !name) {
  console.log('用法: node verify-asar-chunk.cjs <app.asar路径> <chunk文件名>');
  process.exit(1);
}

try {
  const list = asar.listPackage(p).map(x => x.replace(/^\\/, ''));
  const target = list.find(x => x.endsWith(name) || x.includes(name));
  if (!target) {
    console.log(`✗ chunk "${name}" 不在 asar 中`);
    process.exit(1);
  }
  const buf = asar.extractFile(p, target);
  const out = path.join(process.cwd(), name.replace(/[\\/:*?"<>|]/g, '_'));
  fs.writeFileSync(out, buf);
  console.log(`✓ 提取 ${target}: ${buf.length} 字节 -> ${out}`);

  // 语法检查（node --check 只查语法不解析模块）
  try {
    execSync(`node --check "${out}"`, { stdio: 'pipe' });
    console.log('✓ 语法正常 (node --check 通过)');
  } catch (e) {
    console.log('✗ 语法错误: ' + (e.stderr || e.message).toString().slice(0, 200));
  }

  // 依赖链完整性：chunk 里 from"./xxx.js" 的兄弟 chunk 逐一验证可提取
  const imports = [...buf.toString('utf8').matchAll(/from"\.\/([^"]+)"/g)].map(m => m[1]);
  console.log(`依赖 chunk: ${imports.length} 个`);
  let ok = true;
  for (const imp of imports) {
    const found = list.find(x => x.endsWith(imp) || x.includes(imp));
    if (!found) {
      console.log(`  ✗ 缺失: ${imp}`);
      ok = false;
    }
  }
  console.log(ok ? '✓ 依赖链完整' : '✗ 依赖链有缺失');
  if (ok && !fs.existsSync(out)) process.exit(0);
} catch (e) {
  console.log('错误: ' + e.message.slice(0, 300));
  process.exit(1);
}
