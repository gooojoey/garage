#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
公众号爆款标题生成器
====================
基于 wechat-article-writing 技能的 8 种标题模式，给定主题/痛点，批量产出候选标题。

用法示例:
  python generate_titles.py --topic "脱发" --pain "发际线焦虑"
  python generate_titles.py --topic "副业" --pain "工资不够花" --per 3
  python generate_titles.py --examples        # 打印近30天真实爆款标题样例
  python generate_titles.py --topic "AI写作" --check "AI写作,别再迷信日更"  # 按禁忌自检

输出: 每条候选标注所属模式，便于人工筛选与去标题党。
"""
import argparse
import sys

# 八种标题模式 -> 生成函数(topic, pain) -> 候选列表
PATTERNS = {
    "数字痛点": lambda t, p: [
        f"5个关于{t}的误区，90%的人每天都在犯",
        f"坚持30天{t}，我肉眼可见地变好了",
        f"3个{t}方法，解决{p}，亲测有效",
    ],
    "反差反常识": lambda t, p: [
        f"以为{t}很难，其实掌握这一点就行",
        f"别再迷信{t}！我踩坑后才明白这4个道理",
        f"同样在{t}，为什么别人轻松，你却{p}？",
    ],
    "悬念留白": lambda t, p: [
        f"一个危险信号：{t}排第二，{p}竟然排第一…",
        f"关于{t}，90%的人忽略了一件大事…",
        f"这才是{t}的真相，很多人到现在还不知道",
    ],
    "热点权威": lambda t, p: [
        f"最新！关于{t}，官方回应来了",
        f"突发：{t}迎来重大调整，赶紧了解",
        f"{t}新规实施，影响每一个人",
    ],
    "情绪共鸣": lambda t, p: [
        f"人到一定年纪，终于读懂了{t}",
        f"写{t}一年，我快坚持不下去，直到想通这3件事",
        f"那个在{t}里默默坚持的人，让我破防了",
    ],
    "短句口语": lambda t, p: [
        f"{t}，到底值不值得？",
        f"说真的，{t}这件事别再拖了",
        f"关于{t}，我想说句大实话",
    ],
    "民生警示": lambda t, p: [
        f"警惕！{t}正在悄悄伤害你",
        f"{p}？很多人还蒙在鼓里",
        f"紧急提醒：{t}这件事，现在就要做",
    ],
    "公告促销": lambda t, p: [
        f"重磅！{t}限时福利来了",
        f"报告！{t}只要29.9，速抢",
        f"{t}正式开启，手慢无",
    ],
}

# 标题禁忌词（命中需人工复核，易降权/像标题党）
RED_FLAGS = ["暴富", "内幕", "震惊", "曝光", "绝密", "惊天", "必看", "不看后悔"]

EXAMPLES = [
    "刘翔都舍不得编制",
    "旺旺，背刺打工人",
    "以为它高热量，其实少油，减脂人也爱吃。",
    "一个很危险现象：越来越多孩子“脑腐”了，玩手机排第二，排第一竟然是…",
    "烘干机的第一批受害者，已经出现了",
    "成本150元卖2400元！很多人用过！",
    "已致三人永久失明！知名品牌紧急召回百万件相关产品！",
    "9月1日实施！人民币使用新规定",
    "报告！1斤薯条桶、鸡块桶，29.9元！",
    "53岁穿牛仔裙回淄博农村，邻居一句“你怎么这么漂亮”，让我找回了自己",
    "美股开盘：三大指数集体下跌，存储芯片板块下跌，闪迪跌1%，美光科技飘绿",
    "国涛，被查",
]


def generate(topic: str, pain: str = "", per: int = 2):
    out = []
    for name, fn in PATTERNS.items():
        try:
            cands = fn(topic, pain)
        except Exception:
            cands = []
        for c in cands[:per]:
            out.append((name, c))
    return out


def check_title(title: str):
    hits = [w for w in RED_FLAGS if w in title]
    return hits


def main():
    ap = argparse.ArgumentParser(description="公众号爆款标题生成器")
    ap.add_argument("--topic", default="")
    ap.add_argument("--pain", default="")
    ap.add_argument("--per", type=int, default=2, help="每个模式产出条数，默认2")
    ap.add_argument("--examples", action="store_true", help="打印真实爆款标题样例")
    ap.add_argument("--check", default="", help="对给定标题做禁忌词自检")
    args = ap.parse_args()

    if args.examples:
        print("=== 近30天真实爆款标题（2026.8-9）示例 ===")
        for e in EXAMPLES:
            print(" -", e)
        return

    if args.check:
        hits = check_title(args.check)
        if hits:
            print(f"[禁忌预警] 标题含敏感/标题党词: {hits}")
        else:
            print("[OK] 未命中已知禁忌词，但仍需核对内容一致性。")
        return

    if not args.topic:
        print("请提供 --topic，或用 --examples 查看样例、--check 自检标题。")
        sys.exit(1)

    print(f"# 标题候选（主题: {args.topic} / 痛点: {args.pain or '无'}）")
    for name, title in generate(args.topic, args.pain, args.per):
        flag = ""
        hits = check_title(title)
        if hits:
            flag = f"  ⚠ 含词:{hits}"
        print(f"[{name}] {title}{flag}")


if __name__ == "__main__":
    main()
