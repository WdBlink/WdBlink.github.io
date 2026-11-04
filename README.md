# 尹鹏宇 WdBlink 的个人网站

[访问网站](https://wdblink.github.io/)

这里收录我的工作流、Skills、Apps、博客、知识地图和摄影作品。网站由 GitHub Pages 发布。

## 实现与参考

当前版本使用 Jekyll 3.10、Liquid 和原生 HTML、CSS、JavaScript，页面与交互由本仓库的 `studio` 布局实现。

- [al-folio](https://github.com/alshedivat/al-folio) 是个人网站组织方式与主题方向的参考。当前版本没有引入 al-folio 的主题代码或插件运行时。
- [yate.fun](https://yate.fun/) 是排版、配色与克制的手帐感视觉参考。内容与个人身份均为本站自己的资料。

## 本地预览

```sh
bundle install
bundle exec jekyll serve --host 127.0.0.1
```

打开 <http://127.0.0.1:4000/>。

## 内容与布局

- `_posts/` 保存博客原文，保留原日期、作者和文章 URL。
- `_data/studio_skills.json` 保存公开的 Skills 目录。
- `_data/studio_photos.json` 保存摄影尺寸与站内图片路径。`assets/studio/photos/` 仅保存去除 EXIF 元数据、最长边不超过 1920 像素的 10 张压缩网页副本，合计约 4.9 MB。照片原片不存入仓库。
- `assets/studio/content.js` 将 Jekyll 内容生成为前端索引。
- `assets/studio/site.js` 和 `assets/studio/style.css` 实现页面交互与样式。
- `_layouts/studio.html` 和 `_layouts/studio-post.html` 实现站点外框与文章布局。

## 检查

```sh
bundle exec jekyll build --strict_front_matter
bundle exec jekyll doctor
python3 scripts/check_site.py http://127.0.0.1:4000/
```

浏览器检查需要 Python Playwright 及其 Chromium。它检查桌面与手机页面、文章、筛选、导航、图片和摄影弹窗，并阻止、报告站点向七牛发起资源请求。

## 仓库历史与许可

本仓库独立维护，不再作为旧主题的 GitHub fork。迁移保留全部原有分支、标签与提交历史，旧仓库保存在 [WdBlink.github.io-legacy](https://github.com/WdBlink/WdBlink.github.io-legacy)。

历史版本来自 Hux Blog，保留的旧代码与资源仍附有原版权和许可声明。它们不代表当前网站的视觉主题。原许可保存在 [LICENSE](LICENSE)。

- Hux Blog，Copyright (c) 2015-2016 Huxpro，Apache License 2.0。
- Clean Blog Jekyll Theme，Copyright (c) 2013-2016 Blackrock Digital LLC，MIT License，原声明见 `LICENSE`。
- Maple Mono 字体的许可见 [OFL-Maple.txt](assets/studio/OFL-Maple.txt)。

仓库迁移不改变第三方资源的许可，也不改变文章、照片和产品素材各自的授权范围。
