# -*- coding: utf-8 -*-
"""验证两个飞书文档 XML 内容是否零改动（忽略所有标签和空白）。

用法:
    python verify_content_same.py before.xml after.xml

before.xml 必须是修复前用 `docs +fetch --detail with-ids` 拉取的原始 XML，
不要用 markdown 导出做基准（markdown 会渲染 ol 列表序号等，产生假差异）。
两侧都 strip 掉所有标签和空白后逐字符比较，完全一致 = 内容零改动。
"""
import re
import sys


def pure(xml: str) -> str:
    x = re.sub(r"<[^>]+>", "", xml)  # 去标签
    x = re.sub(r"\s+", "", x)  # 去所有空白
    return x


def main() -> int:
    if len(sys.argv) != 3:
        print("用法: python verify_content_same.py <before.xml> <after.xml>")
        return 2
    try:
        a = pure(open(sys.argv[1], encoding="utf-8").read())
        b = pure(open(sys.argv[2], encoding="utf-8").read())
    except FileNotFoundError as e:
        print(f"文件不存在: {e}")
        return 2

    if a == b:
        print(f"OK: 内容零改动（纯文本 {len(a)} 字符完全一致）")
        return 0

    print(f"FAIL: 纯文本不一致 前={len(a)} 后={len(b)}")
    for i, (x, y) in enumerate(zip(a, b)):
        if x != y:
            print(f"第一个差异 @{i}:")
            print(f"  前={a[max(0,i-20):i+20]!r}")
            print(f"  后={b[max(0,i-20):i+20]!r}")
            break
    # 长度差提示
    if len(a) != len(b):
        print(f"长度差 {abs(len(a)-len(b))} 字符——可能有多字/漏字，"
              "若差异集中在 ol 列表序号处，说明对比基准选错了（markdown 导出的序号在 XML 纯文本中不存在）")
    return 1


if __name__ == "__main__":
    sys.exit(main())
