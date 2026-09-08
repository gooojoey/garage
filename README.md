# Garage

## WeChatStickers

微信表情专辑全流程 Skill：先询问风格、设计并确认角色，再制作动态表情与横幅、封面、聊天图标。包含动作连贯、道具语义、固定锚点、真透明背景的检查方法，以及可复现的导出与验证脚本。

- [下载 WeChatStickers.skill](WeChatStickers.skill)
- [Skill 入口](skills/wechat-stickers/SKILL.md)
- [规格与范围](skills/wechat-stickers/references/specifications.md)
- [动作设计与修订](skills/wechat-stickers/references/animation.md)
- [机械导出](skills/wechat-stickers/references/export.md)

显示名为 **WeChatStickers**，目录及调用名为 `wechat-stickers` / `$wechat-stickers`。`.skill` 是 ZIP，解压得到 `wechat-stickers` 目录；支持目录型技能的工具可将其放入相应技能目录。Codex 默认可放在用户的 `.codex/skills/` 下。具体加载方式以目标工具为准。

使用示例：**使用 $wechat-stickers 为我制作一套微信动态表情，先问风格并设计形象，确认后制作表情和专辑物料。** 绘画需要所在环境提供图像生成能力；附带脚本只做已生成素材的机械导出，依赖 Python 3.10+ 与 Pillow，不含模型、不自动抠图、不自动上传微信。规范数值源于用户提供的提交参数，非实时官方认证。包内不含私人照片或历史表情成品。

脚本自测：`python skills/wechat-stickers/scripts/test_export_assets.py`。

## WeChatAccountaste

微信公众号排版审美 Skill。综合早期文艺、生活方式、知识与品牌账号的编辑经验，提供文艺阅读、视觉杂志、清晰行动、创意主题四种模式，同时保留微信可编辑结构与深色模式约束。

- [下载 WeChatAccountaste.skill](WeChatAccountaste.skill)
- [Skill 入口](skills/wechat-accountaste/SKILL.md)
- [审美系统](skills/wechat-accountaste/references/aesthetic-system.md)
- [历史样本与阅读边界](skills/wechat-accountaste/references/source-notes.md)
- [微信兼容规范](skills/wechat-accountaste/references/wechat-compatibility.md)

`.skill` 文件为 ZIP 格式，包含 `wechat-accountaste/SKILL.md` 与三个参考文件。需要目录型 Skill 的工具可解压后使用该目录；具体加载方式以目标工具为准。

参考以2015—2017年为主，部分2019年材料补充。来源包括转存文章、历史分析及部分实际查看的版式图片；未完成所有账号的原生微信版式核验。数值为本 Skill 的设计默认值，不是品牌官方参数。第三方文章与图片未打包。
