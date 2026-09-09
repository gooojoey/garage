# WeChatArticleWriting

把高阅读量公众号文章的写法，整理成可以直接交给 AI 复用的技能。

适合想写公众号推文、起爆款标题、拆解爆文或做新媒体文案的人。它基于 2026 年 8–9 月真实高阅读量文章样本（新榜 10w+ 爆文杂志、微信热点雷达、新榜/清博区域榜单），提炼出标题八模式、正文结构模板和一套写作工作流，输出前先按清单自查。

[下载 WeChatArticleWriting.skill](https://github.com/gooojoey/garage/raw/refs/heads/main/WeChatArticleWriting.skill) · [返回 Garage](https://github.com/gooojoey/garage)

## 能帮你做什么

- 给任意主题起一组高打开率的标题候选，按 8 种模式分类。
- 把一篇推文搭成「SCQA 开头 + 三段式正文 + 结尾催转发」的可读骨架。
- 拆解别人的爆款，反向归纳它为什么火。
- 用自带的生成脚本批量产出标题，并自动检查敏感词 / 标题党。

默认只做写作方法与文案产出，不替你发布到微信；交付后仍应检查实际阅读效果。

## 八种标题模式，按需取用

| 模式 | 更适合 |
| --- | --- |
| 数字 + 痛点 / 清单 | 干货、教程、避坑 |
| 反差 / 反常识 | 观点文、行业观察 |
| 悬念 / 留白 | 故事、揭秘、清单 |
| 热点 + 权威 | 新闻、财经、政务 |
| 情绪共鸣 | 情感、成长、生活感悟 |
| 短句 / 口语 | 八卦、人物、轻松内容 |
| 民生安全警示 | 本地、民生、政策提醒 |
| 公告 / 促销 | 品牌、活动、福利 |

不必先背这些术语。告诉 AI 主题和给谁看，它就会挑合适的模式出标题。

## 你需要提供什么

主题（或一篇想优化的旧文）、目标读者，以及是否要蹭某个热点。有参考文章或风格偏好也可以一起给。

## 可以这样开始

> 使用 WeChatArticleWriting，帮我想 10 个关于「副业」的公众号标题，要带数字和反差点。

拆解爆款时：

> 使用 WeChatArticleWriting，拆解这篇 10 万+ 文章，告诉我它用了哪种标题模式和正文结构。

直接写正文时：

> 使用 WeChatArticleWriting，写一篇关于「年轻人为什么不爱打电话」的推文，情绪共鸣开头，三段式结构。

支持命令式调用的工具可使用 `$wechat-article-writing`。

## 你会得到什么

一组带模式标注的标题、一篇结构完整的推文草稿，或一份爆款拆解。脚本 `scripts/generate_titles.py` 还能在本地批量生成标题并做敏感词自检。

标题决定 80% 的打开率，但内容必须兑现标题承诺，否则取关率会很高。详细方法保留在 [标题模式库](references/title_patterns.md) 与 [正文结构模板](references/article_structures.md)。

安装方式见[仓库首页](https://github.com/gooojoey/garage#怎么使用)。需要支持 Skill 的 AI 工具及文字输出能力；脚本需要 Python 运行环境。

[查看 AI 执行指令](SKILL.md) · [标题模式库](references/title_patterns.md) · [正文结构模板](references/article_structures.md)
