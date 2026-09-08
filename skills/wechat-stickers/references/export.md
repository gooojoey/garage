# 机械导出

Python 3.10+、Pillow（requirements.txt）。脚本不画图、不抠图、不上传、不改全局配置。只有当前工具规则允许本地机械处理才运行。

1. 图像生成/素材工具取得动作图，检查并抠成真透明。
2. 明确每帧裁切框和固定锚点。单张分镜可多次引用。
3. 运行 `python scripts/export_assets.py manifest.json output-v1`，输出目录必须不存在，避免覆盖。
4. 打开 preview.html 实际播放并切换深浅背景。视觉检查通过后另运行 `python scripts/export_assets.py --package output-v1`；导出与打包分开，脚本不伪造人工审核。
5. 修订用新目录；源图、提示词另分类留存。公开技能不附真实项目清单。

清单路径相对清单所在目录；box是原图[左,上,右,下]，anchor是**裁切后**坐标，必须观察后确定，不猜默认。sequence从0开始，明确循环/往返。时长与顺序等长、≥50ms且为10倍数。缩略图取原始帧索引。示例一款用于测试，完整专辑扩展8–24款：

```json
{
  "album": "示例日常",
  "stickers": [{
    "name": "你好",
    "frames": [
      {"path":"sheet.png","box":[0,0,512,512],"anchor":[256,480]},
      {"path":"sheet.png","box":[512,0,1024,512],"anchor":[256,480]},
      {"path":"sheet.png","box":[0,512,512,1024],"anchor":[256,480]},
      {"path":"sheet.png","box":[512,512,1024,1024],"anchor":[256,480]}
    ],
    "sequence":[0,1,2,3,2,1],
    "durations_ms":[250,150,150,350,150,150],
    "thumbnail_frame":3
  }],
  "materials":[
    {"kind":"banner","path":"banner.png"},
    {"kind":"cover","path":"cover-alpha.png"},
    {"kind":"icon","path":"head-alpha.png"}
  ]
}
```

字幕可预先固定排好，或自行用一致字体位置合成；脚本不猜字幕。无字幕也可，不强制每张有字。

materials支持banner、cover、icon、avatar、reward_guide、reward_thanks。banner/reward导出不透明JPG；cover/icon要求透明PNG；avatar保留输入背景。可选crop为源图坐标，先按目标比例裁切而非拉伸，必须检查默认居中裁切是否伤及主体。赞赏GIF需另走动画导出并检查对应尺寸。

输出含gif、thumbnails、materials、preview.html、report.json与清单副本。清单副本仅本地复现，ZIP不带源路径。默认参数来自specifications.md，非实时官方认证。自动检查格式、尺寸、体积、循环和≥4个不同帧；不判断相似度、棋盘纹理、动作语义和自然度。pending_visual_review必须通过真实预览解决，不能仅凭自动结果宣称全通过。
