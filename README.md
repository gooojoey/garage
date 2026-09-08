# Garage

我的 AI 创作工具箱。把日常创作中反复使用的流程整理成 Skill，方便自己复用，也方便分享给别人。

目前有两个技能：一个做微信表情，一个做公众号排版。可以分别下载、独立使用。

## 选一个开始

| 技能 | 适合做什么 | 入口 |
| --- | --- | --- |
| **WeChatStickers** | 从角色形象到动态表情，再到横幅、封面和聊天图标 | [查看介绍](skills/wechat-stickers/) · [下载技能包](https://github.com/gooojoey/garage/raw/refs/heads/main/WeChatStickers.skill) |
| **WeChatAccountaste** | 为已有公众号文章设计图文排版，保留原稿，输出可编辑 HTML | [查看介绍](skills/wechat-accountaste/) · [下载技能包](https://github.com/gooojoey/garage/raw/refs/heads/main/WeChatAccountaste.skill) |

## 怎么使用

1. 选择需要的技能，下载对应的 `.skill` 文件。
2. 在支持 Skill 的 AI 工具中安装。如果工具不支持直接导入，可将文件按 ZIP 解压，再按该工具的方式安装其中的技能目录。
3. 把你的素材和需求交给 AI，并指定使用这个技能。下面两句可以作为起点。

**制作表情包**

> 使用 WeChatStickers，帮我把这张照片设计成一套微信动态表情。先问我喜欢的风格，确认形象后再制作。

**排版公众号文章**

> 使用 WeChatAccountaste，为这篇文章做公众号排版。保留原文，不增加推广语，整体偏简洁的杂志风格。

支持 `$技能名` 的工具也可以使用 `$wechat-stickers` 或 `$wechat-accountaste` 调用。

## 使用前知道这几件事

- Skill 是交给 AI 的工作方法，需要在具备相应能力的工具中使用。表情制作需要图像生成与文件处理能力，公众号排版需要 HTML 输出能力。
- 两个技能都不会自动替你发布到微信。交付后仍应检查最终文件及微信中的实际效果。
- 微信提交要求可能变化，以当前后台为准。技能中的尺寸、排版参数和检查方法是工作起点，不代表平台审核承诺。
- 使用真人照片、品牌形象或第三方图片时，请确认自己有权使用和分享。

## 想看看里面怎么做

每个技能的介绍页面向使用者；`SKILL.md` 是给 AI 执行的指令，`references/` 保存详细方法。WeChatStickers 还附有导出脚本和测试，详见它的[制作与导出说明](skills/wechat-stickers/references/export.md)。

发现问题或有改进建议，欢迎[提交 Issue](https://github.com/gooojoey/garage/issues)。反馈时可附使用工具、预期效果和实际问题；请勿上传密码、证件或未经允许分享的照片。
