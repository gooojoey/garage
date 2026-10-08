#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""中文文笔自检（clinic）

把一段中文里的两类毛病逐项标出来，给出位置与改法提示：

  ① 翻译腔（欧化中文）——万能弱动词、被动泛滥、的的不休、连词堆砌、
     抽象名词、前饰长定语、超长句、空转套话、网络腔设问、说教语气、
     「地」滥用、见 when 就「当」
  ② 文艺腔（文绉绉）——文言虚字、古雅词、古雅颜色词、模板句、
     软化比喻词、公共意象、形容词串

用法
----
    python clinic.py 稿子.txt
    python clinic.py 稿子.txt --json
    type 稿子.txt | python clinic.py -

说明
----
只做体检，不改稿。报告按「硬信号 / 软信号」标注：硬信号建议一律改，
软信号（公共意象、软化比喻词、连词、超长句）用得好可以保留，需人工判断。
对应的完整规则见 references/anti-translation-ese.md 与 references/modern-voice.md。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter

# ---------------------------------------------------------------- 病灶定义

# 1. 万能弱动词（+ 邻近抽象名词）
WEAK_VERB = re.compile(r"(进行|作出|予以|加以|给予|开展|实施|开展|作出)")
WEAK_VERB_FULL = re.compile(
    r"(进行|作出|予以|加以|给予|开展|实施)[^。！？\n，、]{0,8}"
    r"(研究|分析|讨论|处理|优化|决定|贡献|反应|调查|评估|检查|说明|介绍|安排|考虑|调整|"
    r"规范|推动|提高|改善|探讨|探索|沟通|合作|交流|建设|改革|改造|部署|推进|运用|使用|"
    r"执行|落实|总结|汇报|培训|学习|宣传|推广|测算|统计|核实|比对|论证)"
)

# 2. 被动语态
PASSIVE = re.compile(r"(被|由|受到|得以)|为[^。！？\n]{0,6}所")

# 3. 抽象名词
ABSTRACT_NOUN = re.compile(
    r"(可能性|必要性|重要性|可行性|难度|复杂度|有效性|合理性|显著性|系统性|结构性|"
    r"程度|频率|力度|维度|颗粒度|成长性|长期性)"
)

# 4. 冗余连接词
CONJ = re.compile(r"(然而|因此|此外|并且|以及|同时|而且|从而|进而|鉴于|基于)")

# 5. 空转套话
CLICHE = re.compile(
    r"(在当今[^。！？\n]{0,12}的时代|综上所述|总而言之|总的来说|不难看出|不难发现|"
    r"值得一提的是|从某种意义上说|事实上|进一步而言|换句话说|简单来说|"
    r"让我们一起|共同开启|未来可期|赋能|抓手|生态位|闭环|深度赋能|重塑格局)"
)

# 6. 网络腔设问
RHETORICAL = re.compile(r"(你有没有想过|你是否也曾|你是否想过|你可曾想过|你知道吗[，,]?$)")

# ---------------------------------------------------------------- 文艺腔（降调）

# 文言虚字（现代文里出现即为文绉绉；常见成语已排除）
WENYAN_EMPTY = re.compile(
    r"(亦(?!(步亦趋|云亦云))|皆(?!大欢喜)|乃|矣|焉|哉|岂|莫不|可谓|殊为|颇为|不啻|尚且|犹自)"
)

# 古雅形容词（已被用到失效的词）
ARTY_WORD = re.compile(
    r"(氤氲|缱绻|旖旎|阑珊|潋滟|葳蕤|岑寂|婆娑|绰约|缥缈|馥郁|泠泠|菡萏|踟蹰|茕茕|孑然)"
)

# 古雅颜色词
ARTY_COLOR = re.compile(r"(绯|绛|缃|缥|靛|黛|缁|缟|檀|缇)")

# 模板句 / 烂俗四字
TEMPLATE_SENT = re.compile(
    r"(岁月静好|时光温柔|山河远阔|人间清醒|万物可期|向光而行|熠熠生辉|温柔以待|"
    r"如诗如画|五彩斑斓|美轮美奂|风姿绰约|仪态万千|诗和远方|星辰大海)"
)

# 软化比喻词（现代文里宜用「像」或不用）
SOFT_SIMILE = re.compile(r"(仿若|宛如|犹如|恍若|恰似|宛若|好似)")

# 公共意象（用得太多，等于没写）
PUBLIC_IMAGE = re.compile(r"(月光|晚风|星辰|星空|旧巷|灯火|山海|泛黄的|微光|旧时光)")

# 形容词串：连续两个以上「XX的、」
ADJ_LIST = re.compile(r"([一-龥]{2}的[，、]){2,}")

# 7. 保姆式说教
NANNY = re.compile(r"(你可以理解为|简单来说|换句话说|说白了就是|也就是说)")

# 8. 冗余代词
PRONOUN = re.compile(r"(它|其|该|此|上述|这些|那些)")

# 9. 「地」滥用（副词化后缀）
DI = re.compile(r"(成功地|极大地|努力地|认真地|快速地|有效地|明显地|不断地|持续地|充分地|严格地|积极地)")

# 10. 「们」滥用
MEN = re.compile(r"[一二三四五六七八九十百千万数几多]{0,2}[一-龥]{1,3}们")

# 11. 见 when 就「当」（排除 当今/当时/当年/当天/当地/当然/当下/当初 等固定词）
WHEN = re.compile(
    r"当(?!今|时|年|天|地|然|下|初|前|中|务|即|场|众|着|日|夜|空)"
    r"[^。！？\n]{0,15}(的时候|时)"
)

# 12. 前饰长定语（同一名词前两个以上「的」）
LONG_ATTRIB = re.compile(r"[^。！？\n，、]{0,20}的[^。！？\n，、]{1,14}的[^。！？\n，、]{0,6}")

SENT_SPLIT = re.compile(r"[。！？；\n]+")

CLICHE_OPEN = re.compile(r"^(在当今|随着[^。！？\n]{0,15}(的|，)|近年来|如今，)")
CLICHE_END = re.compile(r"(让我们一起|共同开启|未来可期|拭目以待|值得期待|期待您的)[^。！？\n]{0,20}[。！？]?$")


# ---------------------------------------------------------------- 工具函数

def han_len(s: str) -> int:
    """只统计中日韩文字与字母数字，忽略空格。"""
    return len(re.sub(r"\s", "", s))


def sentences(text: str):
    """按句末标点切句，返回 (起始行号, 句长, 句子)。"""
    out = []
    line = 1
    buf = []
    start_line = 1
    for ch in text:
        if ch == "\n":
            if buf:
                s = "".join(buf).strip()
                if s:
                    out.append((start_line, han_len(s), s))
                buf = []
            line += 1
            start_line = line
            continue
        if ch in "。！？；":
            buf.append(ch)
            s = "".join(buf).strip()
            if s:
                out.append((start_line, han_len(s), s))
            buf = []
            start_line = line
            continue
        buf.append(ch)
    if buf:
        s = "".join(buf).strip()
        if s:
            out.append((start_line, han_len(s), s))
    return out


def line_of(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def snippet(text: str, m: re.Match, pad: int = 12) -> str:
    """取命中位置前后文，并用 〘 〙 标出命中处。"""
    a = max(0, m.start() - pad)
    b = min(len(text), m.end() + pad)
    seg = text[a:b].replace("\n", " ")
    i, j = m.start() - a, m.end() - a
    return ("…" if a > 0 else "") + seg[:i] + "〘" + seg[i:j] + "〙" + seg[j:] \
        + ("…" if b < len(text) else "")


# ---------------------------------------------------------------- 检查

def run_checks(text: str):
    findings = []  # (类别, 行号, 提示, 片段, 改法)

    for m in WEAK_VERB_FULL.finditer(text):
        findings.append((
            "万能弱动词", line_of(text, m.start()),
            "「%s…%s」把实义动词拆成了空壳" % (m.group(1), m.group(2)),
            snippet(text, m),
            "还原实义动词：进行研究→研究；作出贡献→贡献很大",
        ))
    for m in WEAK_VERB.finditer(text):
        if not WEAK_VERB_FULL.match(text, m.start()):
            findings.append((
                "万能弱动词", line_of(text, m.start()),
                "出现「%s」" % m.group(1), snippet(text, m),
                "先问一句：那个真动词呢？",
            ))

    for m in PASSIVE.finditer(text):
        findings.append((
            "被动泛滥", line_of(text, m.start()),
            "被动标记", snippet(text, m),
            "改主动，或换用获/遭/挨/受：他被升为营长→他升为营长",
        ))

    for m in ABSTRACT_NOUN.finditer(text):
        findings.append((
            "抽象名词", line_of(text, m.start()),
            "抽象名词「%s」" % m.group(1), snippet(text, m),
            "换成具体动作：用户留存率提升→回头再来的人变多了",
        ))

    # 连接词密度：整句 >= 2 个才算堆砌
    for ln, n, s in sentences(text):
        hits = CONJ.findall(s)
        if len(hits) >= 2:
            findings.append((
                "连词堆砌", ln,
                "一句里 %d 个连接词：%s" % (len(hits), "、".join(sorted(set(hits)))),
                s[:40] + ("…" if len(s) > 40 else ""),
                "删掉一半；删了不通就断成两句",
            ))

    # 的的不休：一句里 >= 3 个「的」
    for ln, n, s in sentences(text):
        c = s.count("的")
        if c >= 3:
            findings.append((
                "的的不休", ln, "一句里 %d 个「的」" % c,
                s[:40] + ("…" if len(s) > 40 else ""),
                "删、挪后（后饰）、或换动词：一个长得像你兄弟的男人→一个男人，长得像你兄弟",
            ))

    # 前饰长定语
    for m in LONG_ATTRIB.finditer(text):
        if m.group(0).count("的") >= 2:
            findings.append((
                "前饰长定语", line_of(text, m.start()),
                "长定语前置", snippet(text, m),
                "定语挪到名词后面，用逗号隔开",
            ))

    # 长句
    for ln, n, s in sentences(text):
        if n > 45:
            findings.append((
                "超长句", ln, "句长 %d 字（阈值 45）" % n,
                s[:36] + "…",
                "拆开；超过 45 字未断句的句子读者会迷失主语",
            ))

    for m in CLICHE.finditer(text):
        findings.append((
            "空转套话", line_of(text, m.start()), "套话", snippet(text, m),
            "直接删掉，从具体的事写起",
        ))

    for m in RHETORICAL.finditer(text):
        findings.append((
            "网络腔设问", line_of(text, m.start()), "设问开头", snippet(text, m),
            "换成具体场景或直接陈述",
        ))

    for m in NANNY.finditer(text):
        findings.append((
            "说教语气", line_of(text, m.start()), "预设读者智商的引导语", snippet(text, m),
            "删掉，直接陈述",
        ))

    for m in DI.finditer(text):
        findings.append((
            "「地」滥用", line_of(text, m.start()), "「%s」" % m.group(1), snippet(text, m),
            "成语或动词作状语不加「地」：努力地学习→努力学习",
        ))

    for m in WHEN.finditer(text):
        findings.append((
            "见when就「当」", line_of(text, m.start()), "「当…的时候」", snippet(text, m),
            "语序自身能表时间：我走进房间，看见他",
        ))

    # ------------------------------------------------------------ 文艺腔
    for m in WENYAN_EMPTY.finditer(text):
        findings.append((
            "文言虚字", line_of(text, m.start()), "「%s」" % m.group(1), snippet(text, m),
            "现代文不用这些虚字，直接删（成语如「皆大欢喜」除外）",
        ))

    for m in ARTY_WORD.finditer(text):
        findings.append((
            "古雅词", line_of(text, m.start()), "「%s」" % m.group(1), snippet(text, m),
            "删掉，直接写那个具体的物或动作",
        ))

    for m in ARTY_COLOR.finditer(text):
        findings.append((
            "古雅颜色词", line_of(text, m.start()), "「%s」" % m.group(1), snippet(text, m),
            "换红/深红/浅黄/淡青/青黑/黑；只在古典题材里保留",
        ))

    for m in TEMPLATE_SENT.finditer(text):
        findings.append((
            "模板句", line_of(text, m.start()), "「%s」" % m.group(1), snippet(text, m),
            "整句删掉，改写一件具体发生的事",
        ))

    for m in SOFT_SIMILE.finditer(text):
        findings.append((
            "软化比喻词", line_of(text, m.start()), "「%s」" % m.group(1), snippet(text, m),
            "换成「像」，或干脆不比喻",
        ))

    for m in PUBLIC_IMAGE.finditer(text):
        findings.append((
            "公共意象", line_of(text, m.start()), "「%s」" % m.group(1), snippet(text, m),
            "全网都在写的意象；换成只有你写得出的私有物象",
        ))

    for m in ADJ_LIST.finditer(text):
        findings.append((
            "形容词串", line_of(text, m.start()), "连续两个以上「XX的」", snippet(text, m),
            "同一名词前只留一个形容词，其余换成动作或物象",
        ))

    # 段落首尾套话
    for i, para in enumerate(text.split("\n")):
        p = para.strip()
        if not p:
            continue
        if CLICHE_OPEN.search(p):
            findings.append(("段落开头套话", i + 1, "开场套话", p[:30] + "…", "删掉，用场景或事实开头"))
        if CLICHE_END.search(p):
            findings.append(("结尾口号", i + 1, "结尾喊口号", p[-30:], "豹尾：短、狠、留余韵"))

    return findings


def stats(text: str):
    sents = sentences(text)
    lens = [n for _, n, _ in sents]
    d = {
        "总字数": han_len(text),
        "句数": len(sents),
        "平均句长": round(sum(lens) / len(lens), 1) if lens else 0,
        "最长句": max(lens) if lens else 0,
        "最短句": min(lens) if lens else 0,
        "「的」总数": text.count("的"),
        "「的」密度(每百字)": round(text.count("的") / max(1, han_len(text)) * 100, 2),
        "「被」总数": text.count("被"),
    }
    # 长短句单调检测：只看「都不短且彼此接近」的三连句；
    # 刻意排布的短句节奏（如汪曾祺）不算单调。
    mono = []
    for i in range(len(lens) - 2):
        w = lens[i:i + 3]
        if min(w) >= 12 and max(w) - min(w) <= 4:
            mono.append((sents[i][0], w))
    d["疑似单调段落(连续三句长度接近)"] = len(mono)
    return d, mono


# ---------------------------------------------------------------- 报告

ORDER = [
    # —— 翻译腔 ——
    "万能弱动词", "被动泛滥", "的的不休", "连词堆砌", "抽象名词",
    "前饰长定语", "超长句", "空转套话", "段落开头套话", "结尾口号",
    "网络腔设问", "说教语气", "「地」滥用", "见when就「当」",
    # —— 文艺腔 ——
    "文言虚字", "古雅词", "古雅颜色词", "模板句", "软化比喻词",
    "公共意象", "形容词串",
]

TRANSLATION_ESE = {
    "万能弱动词", "被动泛滥", "的的不休", "连词堆砌", "抽象名词",
    "前饰长定语", "超长句", "空转套话", "段落开头套话", "结尾口号",
    "网络腔设问", "说教语气", "「地」滥用", "见when就「当」",
}

ARTY_STYLE = {
    "文言虚字", "古雅词", "古雅颜色词", "模板句", "软化比喻词",
    "公共意象", "形容词串",
}


def report(text: str) -> str:
    findings = run_checks(text)
    d, mono = stats(text)

    lines = []
    lines.append("=" * 62)
    lines.append("中文文笔自检报告（clinic）· 翻译腔 + 文艺腔")
    lines.append("=" * 62)
    lines.append("")
    lines.append("【体检数据】")
    for k, v in d.items():
        lines.append("  %-28s %s" % (k, v))
    lines.append("")

    if not findings:
        lines.append("【结论】未检出明显欧化特征。可以进入朗读测试。")
        return "\n".join(lines)

    counter = Counter(f[0] for f in findings)
    tn = sum(c for cat, c in counter.items() if cat in TRANSLATION_ESE)
    an = sum(c for cat, c in counter.items() if cat in ARTY_STYLE)

    lines.append("【病灶分布】")
    lines.append("  ── 翻译腔（结构病）  %d 处 ──" % tn)
    for cat in ORDER:
        if cat in TRANSLATION_ESE and counter.get(cat):
            lines.append("      %-12s %d" % (cat, counter[cat]))
    if not tn:
        lines.append("      （无）")
    lines.append("  ── 文艺腔（调门病）  %d 处 ──" % an)
    for cat in ORDER:
        if cat in ARTY_STYLE and counter.get(cat):
            lines.append("      %-12s %d" % (cat, counter[cat]))
    if not an:
        lines.append("      （无）")
    for cat, c in counter.items():
        if cat not in ORDER:
            lines.append("      %-12s %d" % (cat, c))
    lines.append("")

    # 调门判语：先判断这两种病谁更重，再给对应文件
    if tn >= 3 and an >= 3:
        lines.append("【诊断】两种病同时存在。先祛翻译腔（改结构），再降调（删词）。")
        lines.append("        先看 references/anti-translation-ese.md，再看 references/modern-voice.md。")
        lines.append("")
    elif an >= 3 and an > tn * 1.5:
        lines.append("【诊断】文艺腔重于翻译腔。稿子的问题不是「像机翻」，是「端起来了」。")
        lines.append("        优先做减法：删形容词、删古雅词、删模板句、换掉公共意象。")
        lines.append("        看 references/modern-voice.md 第五节的降调表。")
        lines.append("")
    elif tn >= 3 and tn > an * 1.5:
        lines.append("【诊断】翻译腔重于文艺腔。句子偏欧化：长、被动多、虚词层层叠加。")
        lines.append("        看 references/anti-translation-ese.md。")
        lines.append("")

    lines.append("【逐条明细】")
    cur = None
    for cat, ln, msg, snip, fix in sorted(
        findings, key=lambda x: (x[1], ORDER.index(x[0]) if x[0] in ORDER else 99)
    ):
        if cat != cur:
            cur = cat
            lines.append("")
            lines.append("── %s ──" % cat)
        lines.append("  第 %-3d 行  %s" % (ln, msg))
        lines.append("            片段：%s" % snip)
        lines.append("            改法：%s" % fix)

    if mono:
        lines.append("")
        lines.append("── 节奏单调 ──")
        for ln, w in mono[:8]:
            lines.append("  第 %-3d 行  连续三句长度 %s，读起来会平" % (ln, w))
        lines.append("            改法：把其中一句压成五到七字短句")

    lines.append("")
    lines.append("=" * 62)
    lines.append("信号说明：")
    lines.append("  硬信号（建议一律改）：万能弱动词、被动泛滥、的的不休、文言虚字、")
    lines.append("                       古雅词、古雅颜色词、模板句、形容词串")
    lines.append("  软信号（用得好可保留）：公共意象、软化比喻词、连词、超长句")
    lines.append("最后一步永远是朗读：读着结巴、或者不好意思念出来的地方，就是要改的地方。")
    lines.append("=" * 62)
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="中文欧化自检")
    ap.add_argument("path", help="文本文件路径，或 - 表示从标准输入读取")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    args = ap.parse_args()

    if args.path == "-":
        text = sys.stdin.read()
    else:
        with open(args.path, "r", encoding="utf-8") as f:
            text = f.read()

    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    if args.json:
        d, mono = stats(text)
        print(json.dumps(
            {
                "stats": d,
                "monotony": [{"line": l, "lens": w} for l, w in mono],
                "findings": [
                    {"category": c, "line": l, "message": m, "snippet": s, "fix": f}
                    for c, l, m, s, f in run_checks(text)
                ],
            },
            ensure_ascii=False, indent=2,
        ))
        return 0

    print(report(text))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
