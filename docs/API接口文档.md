# RSS Notice Service - API 接口文档

## 文档信息

- **服务名称**: RSS Notice Service
- **版本**: v1.0.0
- **基础路径**: `http://localhost:8020` 或通过 API Gateway `http://api-gateway:8010/api/rss-notice`
- **创建日期**: 2026-02-10
- **最后更新**: 2026-02-10

---

## 1. 接口概览

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 健康检查 | GET | `/health` | 服务健康状态检查 |
| 检查新文章 | GET | `/api/rss/check` | 检测指定 RSS 源的新文章 |
| 清除缓存 | POST | `/api/rss/refresh` | 清除已处理文章的记录 |
| RSS 源列表 | GET | `/api/rss/sources` | 列出所有配置的 RSS 源 |

---

## 2. 接口详情

### 2.1 健康检查

#### 2.1.1 基本信息

- **接口路径**: `/health`
- **请求方法**: `GET`
- **Content-Type**: `application/json`
- **是否需要认证**: 否

#### 2.1.2 请求示例

```bash
curl http://localhost:8020/health
```

#### 2.1.3 响应示例

**状态码**: 200 OK

```json
{
  "status": "healthy",
  "service": "rss-notice",
  "timestamp": "2026-02-10T12:00:00.000000Z"
}
```

#### 2.1.4 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| status | string | 健康状态：healthy/unhealthy |
| service | string | 服务名称 |
| timestamp | string | 检查时间（ISO 8601 格式） |

---

### 2.2 检查新文章

#### 2.2.1 基本信息

- **接口路径**: `/api/rss/check`
- **请求方法**: `GET`
- **Content-Type**: `application/json`
- **是否需要认证**: 否

#### 2.2.2 请求参数

| 参数 | 类型 | 位置 | 必填 | 说明 |
|------|------|------|------|------|
| tag | string | query | ✅ | RSS 源的 TAG 标识，如 `touzi` |

#### 2.2.3 请求示例

```bash
# 检查 "touzi" 标签的 RSS 源
curl "http://localhost:8020/api/rss/check?tag=touzi"
```

#### 2.2.4 响应示例

**成功响应** - 状态码: 200 OK

```json
{
  "feed_title": "投基有术 - 今天看啥",
  "feed_url": "http://rss.jintiankansha.me/rss/GM4DMMJYHB6DQNLFMRRWCOBRGZSGKNJSMFSWKMZSG4ZDENRQGZQWIYZRGVSTQYTCHAYGMZRVHEYQ====",
  "check_time": "2026-02-10T23:24:48.123456Z",
  "new_count": 3,
  "articles": [
    {
      "id": "a113ffbd1c83c2969a793ba0bd1b69ae",
      "title": "看到了巨机",
      "link": "http://mp.weixin.qq.com/s/rtvedt9caPcvALxWiDb5SQ",
      "published": "2026-02-08T13:39:00Z",
      "author": null,
      "markdown": "📰 公众号「投基有术 - 今天看啥」今日更新\n\n### 看到了巨机\n\n📅 发布：2026-02-08 13:39\n🔗 链接：http://mp.weixin.qq.com/s/rtvedt9caPcvALxWiDb5SQ\n\n---\n"
    }
  ]
}
```

**未找到 TAG** - 状态码: 404 Not Found

```json
{
  "detail": "未找到tag为'xxx'的RSS源，请检查rss_sources.yaml配置"
}
```

**内部错误** - 状态码: 500 Internal Server Error

```json
{
  "detail": "检查失败: RSS 源不可访问"
}
```

#### 2.2.5 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| feed_title | string | 订阅源标题 |
| feed_url | string | 订阅源 URL |
| check_time | string | 检查时间 |
| new_count | int | 新文章数量 |
| articles | array | 文章列表 |

**Article 对象**:

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 文章唯一标识（MD5） |
| title | string | 文章标题 |
| link | string | 文章链接 |
| published | string | 发布时间（ISO 8601） |
| author | string/null | 作者 |
| markdown | string | Markdown 格式信息（可直接发送到钉钉） |

#### 2.2.6 Markdown 格式示例

```markdown
📰 公众号「投基有术 - 今天看啥」今日更新

### 看到了巨机

📅 发布：2026-02-08 13:39
🔗 链接：http://mp.weixin.qq.com/s/rtvedt9caPcvALxWiDb5SQ

---
```

---

### 2.3 清除缓存

#### 2.3.1 基本信息

- **接口路径**: `/api/rss/refresh`
- **请求方法**: `POST`
- **Content-Type**: `application/json`
- **是否需要认证**: 否

#### 2.3.2 请求参数

| 参数 | 类型 | 位置 | 必填 | 说明 |
|------|------|------|------|------|
| tag | string | query | ❌ | RSS 源的 TAG 标识 |
| days | int | query | ❌ | 清除最近 N 天的记录 |

**参数组合**:
- 不传参数：清除所有记录
- 只传 `tag`：清除指定 TAG 的所有记录
- 只传 `days`：清除所有源最近 N 天的记录
- 同时传 `tag` 和 `days`：清除指定 TAG 最近 N 天的记录

#### 2.3.3 请求示例

```bash
# 清除所有记录
curl -X POST "http://localhost:8020/api/rss/refresh"

# 清除指定 TAG 的所有记录
curl -X POST "http://localhost:8020/api/rss/refresh?tag=touzi"

# 清除最近 7 天的所有记录
curl -X POST "http://localhost:8020/api/rss/refresh?days=7"

# 清除最近 30 天的所有记录
curl -X POST "http://localhost:8020/api/rss/refresh?days=30"

# 清除指定 TAG 最近 7 天的记录
curl -X POST "http://localhost:8020/api/rss/refresh?tag=touzi&days=7"
```

#### 2.3.4 响应示例

**成功响应** - 状态码: 200 OK

```json
{
  "status": "success",
  "message": "已清除最近7天的 5 篇文章记录",
  "cleared_count": 5,
  "tag": null,
  "days": 7
}
```

**按 TAG 清除**:
```json
{
  "status": "success",
  "message": "已清除tag为'touzi'的 5 篇文章记录",
  "cleared_count": 5,
  "tag": "touzi"
}
```

**组合参数清除**:
```json
{
  "status": "success",
  "message": "已清除tag为'touzi'的最近30天的 5 篇文章记录",
  "cleared_count": 5,
  "tag": "touzi",
  "days": 30
}
```

**参数错误** - 状态码: 400 Bad Request

```json
{
  "detail": "days参数必须大于0"
}
```

#### 2.3.5 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| status | string | 操作状态：success |
| message | string | 操作结果描述 |
| cleared_count | int | 清除的文章数量 |
| tag | string/null | 清除的 TAG（如果指定） |
| days | int/null | 清除的天数（如果指定） |

---

### 2.4 RSS 源列表

#### 2.4.1 基本信息

- **接口路径**: `/api/rss/sources`
- **请求方法**: `GET`
- **Content-Type**: `application/json`
- **是否需要认证**: 否

#### 2.4.2 请求示例

```bash
curl http://localhost:8020/api/rss/sources
```

#### 2.4.3 响应示例

**成功响应** - 状态码: 200 OK

```json
{
  "count": 1,
  "sources": [
    {
      "tag": "touzi",
      "name": "投基有术",
      "url": "http://rss.jintiankansha.me/rss/GM4DMMJYHB6DQNLFMRRWCOBRGZSGKNJSMFSWKMZSG4ZDENRQGZQWIYZRGVSTQYTCHAYGMZRVHEYQ===="
    }
  ]
}
```

#### 2.4.4 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| count | int | RSS 源总数 |
| sources | array | RSS 源列表 |

**Source 对象**:

| 字段 | 类型 | 说明 |
|------|------|------|
| tag | string | TAG 标识（用于 API 调用） |
| name | string | 公众号/网站名称 |
| url | string | RSS 链接 |

---

## 3. API 变更记录

### 2026-02-10 v1.0.0 - 初始版本

**新增接口**:
- ✅ `GET /health` - 健康检查
- ✅ `GET /api/rss/check` - 检查新文章，支持 `tag` 参数
- ✅ `POST /api/rss/refresh` - 清除缓存，支持 `tag` 和 `days` 参数
- ✅ `GET /api/rss/sources` - RSS 源列表

**参数变更**:
- `/api/rss/check`: 新增必需参数 `tag`
- `/api/rss/refresh`: 新增可选参数 `tag` 和 `days`

**返回值变更**:
- `Article` 对象：移除 `summary` 和 `content` 字段
- `Article` 对象：新增 `markdown` 字段

---

## 4. 错误码说明

| 状态码 | 说明 | 示例场景 |
|--------|------|----------|
| 200 | 成功 | 请求成功处理 |
| 400 | 请求参数错误 | days 参数 ≤ 0 |
| 404 | 资源未找到 | TAG 不存在 |
| 500 | 服务器内部错误 | RSS 源不可访问 |

---

## 5. 使用示例

### 5.1 n8n 集成

**工作流配置**:

1. **定时触发器** (Cron)
   - Cron 表达式: `45 2 * * *`
   - 说明：每天 2:45 执行

2. **HTTP Request**
   - Method: `GET`
   - URL: `http://api-gateway:8010/api/rss-notice/check?tag=touzi`

3. **IF 节点**
   - 条件: `{{$json.new_count > 0}}`
   - 说明：有新文章时继续

4. **钉钉节点**
   - 消息格式: 使用返回的 `articles[].markdown` 字段

### 5.2 常见使用场景

**场景 1: 检查单个 RSS 源**
```bash
curl "http://localhost:8020/api/rss/check?tag=touzi"
```

**场景 2: 定期清理旧数据**
```bash
# 每周清除最近 30 天的记录
curl -X POST "http://localhost:8020/api/rss/refresh?days=30"
```

**场景 3: 重新同步某个源**
```bash
# 先清除该源的所有记录
curl -X POST "http://localhost:8020/api/rss/refresh?tag=touzi"
# 再检查，将获取所有文章
curl "http://localhost:8020/api/rss/check?tag=touzi"
```

---

## 6. API Gateway 路由配置

如果通过 API Gateway 访问，需要在 API Gateway 的 `config/services.yaml` 中添加：

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

**访问路径映射**:
- `http://api-gateway:8010/api/rss-notice/check?tag=touzi` → `http://rss-notice-service:8020/api/rss/check?tag=touzi`
- `http://api-gateway:8010/api/rss-notice/refresh?days=7` → `http://rss-notice-service:8020/api/rss/refresh?days=7`
- `http://api-gateway:8010/api/rss-notice/sources` → `http://rss-notice-service:8020/api/rss/sources`
