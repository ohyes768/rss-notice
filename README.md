# RSS Notice Service

基于 FastAPI 的 RSS 订阅监控服务，符合 API Gateway 规范。

## 功能特性

- ✅ 自动监控 RSS 订阅源
- ✅ 检测新文章并通过 API 返回
- ✅ SQLite 持久化存储，避免重复通知
- ✅ 健康检查接口
- ✅ Docker 容器化部署
- ✅ 集成 API Gateway

## 技术栈

- Python 3.11+
- FastAPI
- uvicorn
- feedparser
- SQLite
- Docker & Docker Compose

## 项目结构

```
rss-notice/
├── src/                        # 服务代码
│   ├── main.py                # FastAPI 应用入口
│   ├── models.py              # 数据模型
│   ├── storage.py             # SQLite 存储
│   ├── rss_fetcher.py         # RSS 拉取
│   ├── config.py              # 配置管理
│   ├── logger.py              # 日志配置
│   ├── Dockerfile             # Docker 镜像
│   ├── requirements.txt       # 依赖列表
│   ├── rss_sources.yaml       # RSS 源配置
│   └── .env                   # 环境变量
├── docker/
│   ├── docker-compose.yml     # Docker Compose 配置
│   └── .env                   # Docker 环境变量
├── data/                      # 数据持久化目录
├── docs/                      # 项目文档
├── discuss/                   # 讨论文档
└── README.md                  # 项目说明
```

## 快速开始

### 1. 创建 Docker 网络（如果不存在）

```bash
docker network create api-gateway_api-network
```

### 2. 启动服务

```bash
cd docker
docker-compose up -d --build
```

### 3. 验证服务

```bash
# 健康检查
curl http://localhost:8020/health

# 检查新文章
curl http://localhost:8020/api/rss/check
```

## API 接口

### 健康检查

```
GET /health
```

响应示例：
```json
{
  "status": "healthy",
  "service": "rss-notice",
  "timestamp": "2026-02-09T12:00:00Z"
}
```

### 检查新文章

```
GET /api/rss/check
```

响应示例：
```json
{
  "feed_title": "今天看啥RSS",
  "feed_url": "http://rss.jintiankansha.me/...",
  "check_time": "2026-02-09T02:45:00",
  "new_count": 3,
  "articles": [
    {
      "id": "abc123...",
      "title": "文章标题",
      "link": "https://...",
      "published": "2026-02-08T10:30:00",
      "author": "作者名",
      "summary": "摘要...",
      "content": null
    }
  ]
}
```

## n8n 集成

### 工作流配置

1. **定时触发器**（Cron）
   - Cron 表达式: `45 2 * * *`（每天 2:45）

2. **HTTP Request 节点**
   - Method: `GET`
   - URL: `http://api-gateway:8010/api/rss-notice/check`

3. **判断节点**（IF）
   - 条件: `{{$json.new_count > 0}}`

4. **钉钉节点**
   - 发送格式化消息到钉钉 Webhook

## API Gateway 配置

在 API Gateway 项目的 `config/services.yaml` 中添加：

```yaml
services:
  rss_notice:
    url: http://rss-notice-service:8020
    enabled: true
    health_path: /health
    routes:
      - path: /api/rss-notice/check
        method: GET
        backend_path: /api/rss/check

      - path: /api/rss-notice/refresh
        method: POST
        backend_path: /api/rss/refresh
```

## 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `RSS_URL` | RSS 订阅链接 | 必填 |
| `DB_PATH` | SQLite 数据库路径 | `/app/data/rss_notice.db` |
| `LOG_LEVEL` | 日志级别 | `INFO` |

## 常见问题

### 1. 如何更换 RSS 源？

修改 `docker/.env` 文件中的 `RSS_URL`，然后重启服务：

```bash
docker-compose restart
```

### 2. 数据存储在哪里？

数据通过 Docker volume 挂载到 `docker/data/` 目录，持久化保存。

### 3. 如何查看日志？

```bash
docker logs -f rss-notice-service
```

## 开发说明

### 本地运行

```bash
cd src
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8020
```

### 依赖管理

使用 uv 管理依赖：

```bash
uv add <package-name>
```

## 许可证

MIT
