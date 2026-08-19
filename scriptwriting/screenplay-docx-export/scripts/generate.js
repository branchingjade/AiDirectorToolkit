// 剧本场景 → Word 文档生成器
// 用法: 把本场次纯文本存到 input.txt, node generate.js → 输出 魔王-第38场.docx
//       修改头部 PROJECT_NAME / SCENE_NO / OUT_FILE 适配其他场次
const fs = require('fs');
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
  Footer, Header, PageNumber
} = require('docx');

// ==== 配置 ====
const PROJECT_NAME = '魔王';
const SCENE_NO = '第38场';
const INPUT = 'input.txt';
const OUT_FILE = '魔王-第38场.docx';
// =============

const raw = fs.readFileSync(INPUT, 'utf8');
const lines = raw.split(/\r?\n/);
const ROLE_RE = /^([^：:（(]{1,8})[：:]\s*(.*)$/;

const blocks = [];
for (const line of lines) {
  const t = line.trim();
  if (!t) continue;
  if (/^\d+(-\d+)?$/.test(t)) { blocks.push({ type: 'num', text: t }); continue; }
  if (/^场\d+/.test(t))      { blocks.push({ type: 'sceneHead', text: t }); continue; }
  if (t.startsWith('△'))     { blocks.push({ type: 'note', text: t.replace(/^△\s*/, '') }); continue; }
  const m = t.match(ROLE_RE);
  if (m)                     { blocks.push({ type: 'dialog', role: m[1].trim(), text: m[2].trim() }); continue; }
  blocks.push({ type: 'action', text: t });
}

const out = [];
for (const b of blocks) {
  if (b.type === 'num') {
    out.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 320, after: 140 },
      children: [new TextRun({ text: b.text, bold: true, size: 28, font: 'SimSun' })] }));
  } else if (b.type === 'sceneHead') {
    out.push(new Paragraph({ heading: HeadingLevel.HEADING_2, alignment: AlignmentType.CENTER, spacing: { before: 220, after: 220 },
      children: [new TextRun({ text: b.text, bold: true, size: 32, font: 'SimHei' })] }));
  } else if (b.type === 'note') {
    out.push(new Paragraph({ spacing: { before: 100, after: 100, line: 340 }, indent: { left: 480 },
      children: [new TextRun({ text: '△ ' + b.text, italics: true, color: '606060', size: 22, font: 'KaiTi' })] }));
  } else if (b.type === 'dialog') {
    out.push(new Paragraph({ spacing: { before: 100, after: 0 }, indent: { left: 480 },
      children: [new TextRun({ text: b.role + '：', bold: true, size: 24, font: 'SimHei' })] }));
    out.push(new Paragraph({ spacing: { before: 0, after: 120, line: 360 }, indent: { left: 720 },
      children: [new TextRun({ text: b.text, size: 24, font: 'SimSun' })] }));
  } else {
    out.push(new Paragraph({ spacing: { before: 80, after: 80, line: 360 }, indent: { firstLine: 480 },
      children: [new TextRun({ text: b.text, size: 24, font: 'SimSun' })] }));
  }
}

const doc = new Document({
  creator: 'Hermes',
  title: `${PROJECT_NAME} ${SCENE_NO}`,
  styles: { default: { document: { run: { font: 'SimSun', size: 24 } } } },
  sections: [{
    properties: { page: { margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
    headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT,
      children: [new TextRun({ text: `《${PROJECT_NAME}》  ${SCENE_NO}`, size: 20, color: '808080', font: 'SimSun' })] })] }) },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [
      new TextRun({ text: '— ', size: 20, color: '808080', font: 'SimSun' }),
      new TextRun({ children: [PageNumber.CURRENT], size: 20, color: '808080', font: 'SimSun' }),
      new TextRun({ text: ' —', size: 20, color: '808080', font: 'SimSun' }),
    ] })] }) },
    children: out,
  }],
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync(OUT_FILE, buf);
  console.log(`OK -> ${OUT_FILE}  (${buf.length} bytes, ${out.length} 段落)`);
});