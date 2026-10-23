# Unextended EC promotional site / 宣传站

Deployed preview / 已部署预览：<https://unextended-wireless-ec.wzuck-wang.chatgpt.site>

The Site starts owner-private. Publishing source to GitHub does not make the hosted preview public. / 站点当前仅所有者可访问；GitHub 源码公开不等于托管预览已经开放访问。

Buildless HTML/CSS/JS in `dist/`, Chinese/English toggle, responsive layout, local CAD renders, engineering-status disclosure, links to firmware, soldering guide and source. No tracking, payment or account backend. No package installation is needed.

`dist/` 内为无构建依赖的 HTML/CSS/JS，包含中英文切换、响应式排版、CAD 渲染、工程状态和文档链接；没有统计追踪、支付或账户后端。

Local preview / 本地预览：

```
python3 -m http.server 8778 --bind 127.0.0.1 --directory website/dist
```

Open <http://127.0.0.1:8778>. JavaScript check: `node --check website/dist/app.js`.

`.openai/hosting.json` retains the hosting identity. Use the Sites source workflow from an isolated copy of `website/` when synchronizing hosting, so its Git metadata does not become an embedded repository in this hardware checkout. Never save credentials in either checkout. Preserve the audience unless explicitly changed.

托管身份保存在 `.openai/hosting.json`。同步托管源时，从 `website/` 的独立副本运行 Sites 流程，避免在硬件仓库内产生嵌套 Git 仓库；不要保存凭据，不应自动修改访问范围。
