# rss-stack：X/B站博主监控 → 飞书群推送 → 智能体日报

自建 RSS 信息源流水线：**RSSHub（双 token 轮换）+ Miniflux + relay 中转 → 飞书群卡片推送 → 触发智能体整理日报 → 飞书文档每日归档**。

Docker Compose 一键部署，全部组件本机自持。

## 架构

```
X 博主 / B站 UP主 / aihot 热点 / Follow Builders 聚合
        ↓ Miniflux 定时轮询（60~120 分钟）
RSSHub（B站路由走无头浏览器）
        ↓ webhook
feishu-relay（卡片组装 / 过滤 / 失败告警 / 定时调度）
        ↓
飞书群卡片推送 → 以用户身份私聊触发智能体整理日报
        ↓
飞书文档按日归档（历史可回查）
```

## 组件

| 容器 | 用途 | 端口 |
|---|---|---|
| rsshub (chromium-bundled) | 生成 RSS（X 走双 token 轮换代理；B站走无头浏览器+登录 Cookie） | 1201 |
| miniflux + miniflux-db | 订阅管理 / 定时轮询 / 条目存储 / webhook 触发 | 8088 |
| feishu-relay | 自写中转：卡片组装、飞书推送、私聊触发智能体、定时场次、失败告警 | 7070 |

## 快速开始

见 [迁移说明.md](迁移说明.md)（含新机部署/数据库恢复/日常运维全流程）。

配置模板见 [.env.example](.env.example) 与 [feishu.env.example](feishu.env.example)。

## 信息源

| 类型 | 数量 | 采集方式 |
|---|---|---|
| X 博主 | 11 | RSSHub twitter 路由，双 auth_token 轮换池 |
| B站 UP 主 | 10 | RSSHub bilibili 路由（chromium + 登录 Cookie），需出口 IP 为国内 |
| aihot 热点 | 1 | aihot.news/feed.xml |
| Follow Builders 聚合 | 3 | GitHub Actions 每日聚合 JSON，relay 转换为 RSS |

## 防风控要点

- X：轮询 60~120 分钟（约 10 次/小时，低于真人）；**auth_token 的提取环境与运行环境出口 IP 必须一致**（否则异地跳变触发会话吊销）；双小号轮换池兜底
- B站：登录 Cookie（SESSDATA+buvid3）+ 国内直连出口；对空间 API 的间歇性 -403 风控，等待自然恢复即可（RSSHub 缓存持有完整列表，不丢数据）

## 监控与告警

- relay 每 30 分钟体检 X 源：≥3 源连续两轮失败 → ⚠️ 告警卡（含恢复指引）发群；恢复后自动发 ✅
- 定时场次自动：总览源增量卡 → 文档归档（末场）→ 私聊触发智能体日报

## License

MIT
