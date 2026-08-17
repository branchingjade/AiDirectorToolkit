#!/usr/bin/env python3
"""按任务类别统计 Hermes token 消耗与费用（人民币）。

用法: python task-cost-classify.py [YYYY-MM]   （默认本月）
直连只读 state.db（不复制，WAL 安全）。无标题会话（子代理）用首条 user 消息归类。
费用按 DeepSeek 官方人民币价（2026-08）：flash 命中0.02/未命中1/输出2，pro 0.025/3/6（元/百万tokens）。
"""
import sqlite3, re, collections, sys
from datetime import date

DB = 'file:C:/Users/HMSJ/AppData/Local/hermes/state.db?mode=ro'
PRICE = {
    'deepseek-v4-flash': (0.02, 1.0, 2.0),
    'deepseek-v4-pro':   (0.025, 3.0, 6.0),
}

def cny_cost(model, it, ot, cr):
    p = PRICE.get(model)
    if not p:
        return 0.0
    hit, miss, out = p
    return (cr or 0)/1e6*hit + (it or 0)/1e6*miss + (ot or 0)/1e6*out

CATS = [
    (r'(提示词|prompt|Seedance|生图|AI提示词|分镜脚本|镜头提示|画面提示)', '提示词优化'),
    (r'(伏妖记|犬子无双|导演|编剧|剧本|短剧|电影|分场|台本|达芬奇|人名条|OGraf|品鉴|韩老爷|陈强|铁北|萧烬|金玄|魔王|神域|白泽|Blender|场景|角色设计)', '影视创作'),
    (r'(TTS|语音|朗读|豆包|音频|配乐|音乐|音色|配音|歌词|音分|声音设计)', '语音音频'),
    (r'(文档|API|MDN|总结|分类|统计|整理)', '文档整理'),
    (r'(排查|修复|Hermes|gateway|配置|升级|补丁|监控|cron|看板|故障|兜底|部署|MCP|Clash|alist|NAS|Eagle|token|网关|WebBridge|浏览器|扩展|busy|wingit|WPS|Viking|git push|卸载|缓存|同步|重启|任务|检查)', '运维排查'),
    (r'(手法体系深化|研习|技能|skill|知识库|大师|题材|美学|专题|科恩|黑泽明|贾樟柯|伯格曼|今敏|姜文|杜琪峰|吴宇森|徐克|胡金铨|王家卫|塔可夫斯基|费里尼|库布里克|诺兰|希区柯克|奉俊昊|杨德昌|李安|宫崎骏|芬奇|斯科塞斯|昆汀|斯皮尔伯格|陈凯歌|李翰祥|谢晋|安德森|费穆|维伦纽瓦|波兰斯基|科波拉|林奇|阿巴斯|特吕弗|卓别林|是枝裕和|张艺谋)', '知识库研习'),
    (r'(飞书|评论|会话|成员|画像|协作|记忆|Obsidian|测试|系统|正常|确认|在吗|问候)', '飞书协作/系统测试'),
]

def classify(title, first_msg):
    t = (title or '') + ' || ' + (first_msg or '')
    for pat, name in CATS:
        if re.search(pat, t, re.I):
            return name
    return '其他'

def next_month_start(y, m):
    if m == 12:
        return f'{y+1:04d}-01-01 00:00:00'
    return f'{y:04d}-{m+1:02d}-01 00:00:00'

def main():
    month = sys.argv[1] if len(sys.argv) > 1 else date.today().strftime('%Y-%m')
    y, m = month.split('-')
    y, m = int(y), int(m)
    db = sqlite3.connect(DB, uri=True)
    cur = db.cursor()
    rows = cur.execute('''SELECT s.id, s.title, s.input_tokens, s.output_tokens,
        s.cache_read_tokens, s.model
        FROM sessions s
        WHERE s.started_at >= strftime('%s', ?) AND s.started_at < strftime('%s', ?)''',
        (f'{y:04d}-{m:02d}-01 00:00:00', next_month_start(y, m))).fetchall()
    first_msgs = {}
    for sid, content in cur.execute("SELECT session_id, content FROM messages WHERE role='user' ORDER BY id"):
        if sid not in first_msgs:
            first_msgs[sid] = (content or '')[:300]
    agg = collections.defaultdict(lambda: [0, 0, 0, 0.0])
    for sid, title, it, ot, cr, model in rows:
        name = classify(title, first_msgs.get(sid, ''))
        a = agg[name]
        a[0] += 1
        a[1] += (it or 0) + (ot or 0)
        a[2] += (cr or 0)
        a[3] += cny_cost(model, it, ot, cr)
    print(f"{'类别':<14}{'会话':>5}{'非缓存tokens(M)':>14}{'缓存(M)':>10}{'费用(元)':>10}")
    for name, (c, tok, cr, cost) in sorted(agg.items(), key=lambda x: -x[1][3]):
        print(f'{name:<14}{c:>5}{tok/1e6:>14.1f}{cr/1e6:>10.1f}{cost:>10.2f}')
    total_s, total_t, total_c = (sum(a[i] for a in agg.values()) for i in (0, 1, 3))
    print(f'\n{month} 总计: {total_s}会话, {total_t/1e6:.1f}M 非缓存tokens, {total_c:.2f} 元')

if __name__ == '__main__':
    main()
