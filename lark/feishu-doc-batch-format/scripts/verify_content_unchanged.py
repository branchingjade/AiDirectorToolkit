#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证飞书文档格式修复前后内容零改动。

对比两个 `lark-cli docs +fetch --detail with-ids --format json` 输出的
content 字段（去标签 + 去空白后的纯文本），完全一致则内容零改动。

用法:
    python verify_content_unchanged.py <before.json> <after.json>

注意:
    - 两个文件都必须是 with-ids 的 XML fetch 输出（json 信封）
    - 不要用 markdown 导出对比——ol 列表序号、转义会造成假差异
    - 返回码 0 = 一致，1 = 有差异，2 = 参数错误
"""
import json
import re
import sys


def pure(x):
    x = re.sub(r'<[^>]+>', '', x)
    x = re.sub(r'\s+', '', x)
    return x


def load_content(path):
    with open(path, encoding='utf-8') as f:
        d = json.load(f)
    return d['data']['document']['content']


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        return 2

    before = pure(load_content(sys.argv[1]))
    after = pure(load_content(sys.argv[2]))

    print(f'修复前纯文本长度: {len(before)}')
    print(f'修复后纯文本长度: {len(after)}')

    if before == after:
        print('OK: 内容零改动，完全一致')
        return 0

    # 找第一个差异位置
    for i in range(min(len(before), len(after))):
        if before[i] != after[i]:
            print(f'FAIL: 第一个差异 @{i}')
            print(f'  前: ...{before[max(0, i-20):i+20]}...')
            print(f'  后: ...{after[max(0, i-20):i+20]}...')
            return 1
    print(f'FAIL: 长度不同（前 {len(before)} vs 后 {len(after)}），公共前缀完全一致')
    return 1


if __name__ == '__main__':
    sys.exit(main())
