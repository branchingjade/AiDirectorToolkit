#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""妖玉影视知识库 · 卡片可达性自检脚本

双向审计：
  正向（卡片→入口）：每张卡是否被检索表/索引表覆盖（创作时查得到）
  反向（入口→卡片）：检索表/索引表/速查表引用的卡片是否都存在（引用不悬空）

用法：
    python3 scripts/card_reachability_check.py            # 检查 skill 正本
    python3 scripts/card_reachability_check.py --kb <path>  # 指定 _知识库 路径

退出码：0 = 全部通过；1 = 存在缺口
"""
import os
import re
import sys

def main():
    kb = None
    args = sys.argv[1:]
    for i, a in enumerate(args):
        if a == '--kb' and i + 1 < len(args):
            kb = args[i + 1]
    if kb is None:
        # 默认：本脚本位于 _知识库/scripts/ 下，向上两级即 _知识库 根
        kb = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    kb = os.path.abspath(kb)

    skill_path = os.path.join(kb, 'SKILL.md')
    if not os.path.exists(skill_path):
        print('❌ 未找到 SKILL.md: %s' % skill_path)
        return 1

    kb_skill = open(skill_path, encoding='utf-8').read()

    # ---- 收集全部卡片文件 ----
    card_names = set()
    jc_dir = os.path.join(kb, 'references', '大师技法卡片')
    if os.path.isdir(jc_dir):
        for f in os.listdir(jc_dir):
            if f.endswith('_技法卡片.md'):
                card_names.add(f[:-len('_技法卡片.md')])
    da_dir = os.path.join(kb, 'references', '导演美学卡片')
    if os.path.isdir(da_dir):
        for f in os.listdir(da_dir):
            if f.endswith('_导演美学卡片.md'):
                card_names.add(f[:-len('_导演美学卡片.md')])
            elif f.endswith('_手法体系深化.md'):
                card_names.add(f[:-len('_手法体系深化.md')])

    # ---- 已知别名（卡名简称/全名）----
    ALIASES = {
        '大卫·芬奇': '芬奇', '阿甘': '阿甘正传', '聂小倩剑袋': '倩女幽魂',
        '聂小倩': '倩女幽魂', '大红灯笼': '大红灯笼高高挂',
        '刘伟强': None, '麦兆辉': None, '彼得·威尔': None,  # 无卡导演（索引表已标注查技法卡）
        '伏妖记': None,  # 项目实战，非库卡
    }

    def table_rows(header_pattern):
        m = re.search(header_pattern + r'.*?\n(.*?)(?=\n## )', kb_skill, re.S)
        if not m:
            return []
        return [l for l in m.group(1).splitlines() if l.strip().startswith('|')]

    def extract_names(cell):
        names = set()
        cell = re.sub(r'[（(][^）)]*[）)]', '', cell)
        cell = cell.replace('[手法体系深化]', '').replace('[手法深化]', '')
        for part in re.split(r'[/、,，;；\s]+', cell):
            part = part.strip()
            if part and len(part) >= 2 and not part.isdigit():
                names.add(part)
        return names

    def resolve(name):
        # 先剥卡片编号（聂小倩卡片2 → 聂小倩）
        bare = re.sub(r'卡片\d+$', '', name)
        if bare in ALIASES:
            return ALIASES[bare]
        return bare

    errors = []

    # ---- 反向审计：引用列 → 卡片存在 ----
    scene_rows = table_rows(r'## 场景类型')
    dir_rows = table_rows(r'## 导演美学卡片索引')
    skill_rows = table_rows(r'## 核心招式速查')

    # 表头/分隔行识别：含列标题词或全为分隔符
    HEADER_CELLS = {'场景', '要拍什么', '查哪张卡片', '查哪位导演', '可复用技法',
                    '核心可学', '场景类型', '出处', '招式', '一句话落法', '题材密码'}

    for label, rows, col in [('场景检索表', scene_rows, 2),
                             ('导演索引表', dir_rows, 2),
                             ('核心招式速查', skill_rows, 4)]:
        for row in rows:
            cells = [c.strip() for c in row.split('|')]
            if len(cells) <= col:
                continue
            cell = cells[col]
            if set(cell) <= {'-', ':'}:
                continue
            if cell in HEADER_CELLS:
                continue  # 表头行
            for name in extract_names(cell):
                base = resolve(name)
                if base and base not in card_names:
                    errors.append('[反向] %s 引用「%s」但无卡片文件' % (label, name))

    # ---- 正向审计：卡片 → 入口 ----
    table_text = '\n'.join(scene_rows + dir_rows)
    no_entry = []
    for name in sorted(card_names):
        if name not in table_text:
            no_entry.append(name)

    # ---- 报告 ----
    print('知识库卡片总量: %d（技法+美学+深化）' % len(card_names))
    print('反向引用检查: 场景检索表 %d 行 / 导演索引表 %d 行 / 核心招式速查 %d 行'
          % (len(scene_rows), len(dir_rows), len(skill_rows)))
    print('反向断链: %d' % len(errors))
    for e in errors:
        print('  ❌ ' + e)
    print('正向无入口: %d' % len(no_entry))
    for n in no_entry:
        print('  ⚠️ %s' % n)

    if not errors and not no_entry:
        print('\n✅ 卡片可达性全部通过')
        return 0
    print('\n⚠️ 存在缺口，需修复')
    return 1

if __name__ == '__main__':
    sys.exit(main())
