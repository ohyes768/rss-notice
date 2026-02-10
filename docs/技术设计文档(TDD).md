# RSS Notice Service - 技术设计文档 (TDD)

## 文档信息

- **项目名称**: RSS Notice Service
- **版本**: v1.0.0
- **创建日期**: 2026-02-10
- **最后更新**: 2026-02-10

---

## 1. 系统架构

### 1.1 架构概览

```
┌─────────┐      ┌──────────────┐      ┌──────────┐
│   n8n   │─────▶│ API Gateway  │─────▶│  RSS API │
│ Workflow│      │  (可选)       │      │  Service │
└─────────┘      └──────────────┘      └──────────┘
                                                │
                                                ▼
                                        ┌──────────────┐
                                        │   SQLite     │
                                        │   Storage    │
                                        └──────────────┘
                                                │
                                                ▼
                                        ┌──────────────┐
                                        │ RSS Sources  │
                                        │  (YAML)      │
                                        └──────────────┘
```

### 1.2 技术栈

| 组件 | 技术选型 | 版本 | 说明 |
|------|---------|------|------|
| Web 框架 | FastAPI | 0.104+ | 高性能异步框架 |
| ASGI 服务器 | Uvicorn | 0.24+ | ASGI 服务器 |
| RSS 解析 | feedparser | 6.0+ | RSS/Atom 解析库 |
| 数据验证 | Pydantic | 2.5+ | 数据验证和序列化 |
| 数据库 | SQLite | 3.x | 嵌入式数据库 |
| 配置管理 | YAML + python-dotenv | - | YAML 配置 + 环境变量 |
| 容器化 | Docker + Docker Compose | - | 容器部署 |
| 包管理 | uv | - | Python 包管理器 |

### 1.3 项目结构

```
rss-notice/
├── backend/
│   └── rss_notice_service/
│       ├── __init__.py
│       ├── main.py              # FastAPI 应用入口
│       ├── models.py            # Pydantic 数据模型
│       ├── storage.py           # SQLite 持久化存储
│       ├── rss_fetcher.py       # RSS 拉取和解析
│       ├── config.py            # 配置管理
│       ├── logger.py            # 日志配置
│       ├── Dockerfile           # Docker 镜像
│       ├── requirements.txt     # 依赖列表
│       ├── rss_sources.yaml    # RSS 源配置
│       └── .env                 # 环境变量
├── docker/
│   ├── docker-compose.yml      # Docker Compose 配置
│   └── .env                     # Docker 环境变量
├── data/                       # 数据存储目录
├── docs/                       # 项目文档
├── discuss/                    # 讨论文档
└── README.md                   # 项目说明
```

---

## 2. 核心模块设计

### 2.1 API 接口模块 (main.py)

**职责**: FastAPI 应用入口，定义所有 API 端点

**核心接口**:
```python
# 健康检查
GET /health

# 检查新文章（核心接口）
GET /api/rss/check?tag={tag}

# 清除缓存
POST /api/rss/refresh?tag={tag}&days={days}

# 列出所有 RSS 源
GET /api/rss/sources
```

**关键实现**:
- 使用 `Query` 参数解析查询字符串
- 异常处理和错误响应
- 统一的响应格式

### 2.2 数据模型模块 (models.py)

**职责**: 定义 Pydantic 数据模型，提供类型验证

**核心模型**:
```python
class Article(BaseModel):
    id: str              # 文章唯一标识 (MD5)
    title: str           # 文章标题
    link: str            # 文章链接
    published: Optional[datetime]  # 发布时间
    author: Optional[str]          # 作者
    markdown: str        # Markdown 格式信息

class RSSCheckResponse(BaseModel):
    feed_title: str      # 订阅源标题
    feed_url: str        # 订阅源 URL
    check_time: datetime # 检查时间
    new_count: int       # 新文章数量
    articles: List[Article]  # 文章列表
```

**设计要点**:
- 强类型约束
- 自动 JSON 序列化
- datetime 格式化

### 2.3 存储模块 (storage.py)

**职责**: SQLite 数据库操作，持久化文章记录

**核心方法**:
```python
class Storage:
    def is_article_processed(self, article_id: str, tag: str) -> bool
    def save_articles(self, articles: list, tag: str) -> int
    def clear_all_articles(self, tag: str = None) -> int
    def clear_articles_by_days(self, days: int, tag: str = None) -> int
```

**数据库表结构**:
```sql
CREATE TABLE articles (
    id TEXT PRIMARY KEY,     -- 文章 ID (MD5)
    tag TEXT NOT NULL,        -- RSS 源标识
    title TEXT NOT NULL,      -- 文章标题
    link TEXT NOT NULL,       -- 文章链接
    published TEXT,           -- 发布时间
    author TEXT,              -- 作者
    created_at TEXT NOT NULL  -- 创建时间
);
```

**设计要点**:
- 使用上下文管理器 (`with`) 自动关闭连接
- 支持按 tag 区分不同 RSS 源
- 自动迁移旧数据（添加 tag 列）

### 2.4 RSS 拉取模块 (rss_fetcher.py)

**职责**: 解析 RSS 源，提取文章信息

**核心方法**:
```python
class RSSFetcher:
    def _generate_article_id(self, article_link: str) -> str
    def _generate_markdown(self, title, link, published, feed_title) -> str
    def fetch_new_articles(self, rss_url: str, tag: str) -> Dict
```

**处理流程**:
1. 使用 `feedparser` 解析 RSS
2. 提取文章元数据（标题、链接、时间等）
3. 生成 Markdown 格式输出
4. 对比数据库，过滤新文章

**设计要点**:
- 文章 ID 使用 MD5(article_link) 生成
- 错误处理：解析失败的文章跳过
- 日志记录：记录解析进度和结果

### 2.5 配置管理模块 (config.py)

**职责**: 加载和管理配置

**配置来源**:
1. 环境变量 (.env 文件)
2. YAML 配置文件 (rss_sources.yaml)

**核心方法**:
```python
class Config:
    def get_rss_source(self, tag: str) -> Optional[Dict]
    def get_rss_url(self, tag: str) -> Optional[str]
    def get_rss_name(self, tag: str) -> Optional[str]
```

**YAML 配置格式**:
```yaml
sources:
  touzi:
    name: "投基有术"
    url: "http://rss.jintiankansha.me/rss/..."
```

---

## 3. 数据模型设计

### 3.1 文章模型 (Article)

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string | ✅ | 文章唯一标识，MD5(链接) |
| title | string | ✅ | 文章标题 |
| link | string | ✅ | 文章链接 |
| published | datetime | ❌ | 发布时间 |
| author | string | ❌ | 作者 |
| markdown | string | ✅ | Markdown 格式信息 |

### 3.2 RSS 源配置模型

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| tag | string | ✅ | 唯一标识 |
| name | string | ✅ | 公众号名称 |
| url | string | ✅ | RSS 链接 |

---

## 4. 接口设计

### 4.1 健康检查接口

```
GET /health
```

**响应**:
```json
{
  "status": "healthy",
  "service": "rss-notice",
  "timestamp": "2026-02-10T12:00:00Z"
}
```

### 4.2 检查新文章接口

```
GET /api/rss/check?tag={tag}
```

**请求参数**:
- `tag` (string, 必需): RSS 源的 TAG 标识

**响应**:
```json
{
  "feed_title": "投基有术 - 今天看啥",
  "feed_url": "http://rss.jintiankansha.me/rss/...",
  "check_time": "2026-02-10T12:00:00Z",
  "new_count": 3,
  "articles": [
    {
      "id": "abc123...",
      "title": "文章标题",
      "link": "https://...",
      "published": "2026-02-08T10:30:00Z",
      "author": null,
      "markdown": "📰 公众号「投基有术」今日更新\n\n### 文章标题\n\n..."
    }
  ]
}
```

### 4.3 清除缓存接口

```
POST /api/rss/refresh?tag={tag}&days={days}
```

**请求参数**:
- `tag` (string, 可选): RSS 源标识
- `days` (int, 可选): 清除最近 N 天的记录

**响应**:
```json
{
  "status": "success",
  "message": "已清除最近7天的 5 篇文章记录",
  "cleared_count": 5,
  "tag": null,
  "days": 7
}
```

### 4.4 RSS 源列表接口

```
GET /api/rss/sources
```

**响应**:
```json
{
  "count": 1,
  "sources": [
    {
      "tag": "touzi",
      "name": "投基有术",
      "url": "http://rss.jintiankansha.me/rss/..."
    }
  ]
}
```

---

## 5. 数据存储设计

### 5.1 数据库表结构

**articles 表**:
```sql
CREATE TABLE articles (
    id TEXT PRIMARY KEY,         -- 文章 ID
    tag TEXT NOT NULL,           -- RSS 源标识
    title TEXT NOT NULL,         -- 标题
    link TEXT NOT NULL,          -- 链接
    published TEXT,              -- 发布时间 (ISO格式)
    author TEXT,                 -- 作者
    created_at TEXT NOT NULL     -- 记录创建时间
);

-- 索引
CREATE INDEX idx_tag ON articles(tag);
CREATE INDEX idx_created_at ON articles(created_at);
```

### 5.2 数据迁移

**旧版本升级（添加 tag 列）**:
```python
# 检查表结构
cursor = conn.execute("PRAGMA table_info(articles)")
columns = [row[1] for row in cursor.fetchall()]

# 如果没有 tag 列，则添加
if 'tag' not in columns:
    conn.execute("ALTER TABLE articles ADD COLUMN tag TEXT DEFAULT 'default'")
    conn.commit()
```

---

## 6. 部署设计

### 6.1 Docker 容器化

**Dockerfile**:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8020
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8020/health || exit 1
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8020"]
```

**docker-compose.yml**:
```yaml
version: '3.8'
services:
  rss-notice-service:
    build: ../backend/rss_notice_service
    container_name: rss-notice-service
    ports:
      - "8020:8020"
    environment:
      - DB_PATH=/app/data/rss_notice.db
      - LOG_LEVEL=INFO
    volumes:
      - ./data:/app/data
    networks:
      - api-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8020/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### 6.2 API Gateway 集成

**services.yaml 配置**:
```yaml
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
    - path: /api/rss-notice/sources
      method: GET
      backend_path: /api/rss/sources
```

---

## 7. 技术实现更新

### 2026-02-10 v1.0.0 - 初始版本

**新增模块**:
- ✅ main.py: FastAPI 应用，4 个 API 端点
- ✅ models.py: 3 个 Pydantic 模型
- ✅ storage.py: SQLite 操作类，支持 tag 参数
- ✅ rss_fetcher.py: RSS 解析，Markdown 生成
- ✅ config.py: YAML 配置加载
- ✅ logger.py: 日志配置

**架构设计**:
- 微服务架构，符合 API Gateway 规范
- 容器化部署，Docker Compose 编排
- SQLite 持久化存储
- 多 RSS 源支持，通过 TAG 区分

**关键实现**:
- 文章去重：MD5(article_link)
- 按时间清理：使用 `created_at >= cutoff_time` 条件
- Markdown 输出：友好格式，适合钉钉
- 自动迁移：检测并添加 tag 列
