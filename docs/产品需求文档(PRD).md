# RSS Notice Service - 产品需求文档 (PRD)

## 文档信息

- **项目名称**: RSS Notice Service
- **版本**: v1.0.0
- **创建日期**: 2026-02-10
- **最后更新**: 2026-02-10

---

## 1. 产品概述

### 1.1 产品定位

RSS Notice Service 是一个基于 FastAPI 的微服务，用于监控多个 RSS 订阅源，检测新文章并通知用户。该服务通过 API Gateway 暴露 RESTful API，由 n8n 工作流定时调用，将新文章信息发送到钉钉等消息平台。

### 1.2 核心价值

- ✅ **自动监控**: 自动检测 RSS 源的新文章
- ✅ **智能去重**: 避免重复通知同一篇文章
- ✅ **多源支持**: 支持同时监控多个公众号/网站
- ✅ **灵活配置**: 通过 YAML 配置文件管理多个 RSS 源
- ✅ **友好输出**: Markdown 格式，适合发送到钉钉

### 1.3 目标用户

- 个人用户：监控个人关注的公众号更新
- 团队用户：团队知识库、资讯汇总
- n8n 用户：作为 n8n 工作流的数据源

---

## 2. 功能需求

### 2.1 核心功能

#### 2.1.1 RSS 源管理

**功能描述**: 支持配置和管理多个 RSS 订阅源

**用户场景**:
- 用户可以添加多个公众号的 RSS 链接
- 为每个 RSS 源设置唯一的 TAG 标识
- 通过 API 查询所有已配置的 RSS 源

**配置方式**:
```yaml
# rss_sources.yaml
sources:
  touzi:
    name: "投基有术"
    url: "http://rss.jintiankansha.me/rss/..."
```

#### 2.1.2 新文章检测

**功能描述**: 检测指定 RSS 源的新文章

**用户场景**:
- n8n 定时调用 API 检查新文章
- 返回自上次检查以来新增的文章
- 避免重复通知已读文章

**API 调用**:
```
GET /api/rss/check?tag=touzi
```

#### 2.1.3 缓存管理

**功能描述**: 管理已处理文章的缓存记录

**用户场景**:
- 清除特定 TAG 的缓存（重新同步该源）
- 清除指定天数的缓存（定期清理旧数据）
- 清除所有缓存（完全重置）

**API 调用**:
```
# 清除指定 TAG 的所有缓存
POST /api/rss/refresh?tag=touzi

# 清除最近 7 天的缓存
POST /api/rss/refresh?days=7

# 清除指定 TAG 最近 30 天的缓存
POST /api/rss/refresh?tag=touzi&days=30
```

### 2.2 辅助功能

#### 2.2.1 健康检查

**功能描述**: 提供服务健康状态检查接口

**用途**: Docker 容器健康检查、负载均衡器探测

**API 调用**:
```
GET /health
```

#### 2.2.2 RSS 源列表

**功能描述**: 列出所有已配置的 RSS 源

**用途**: 查看当前可用的 RSS 源和 TAG 标识

**API 调用**:
```
GET /api/rss/sources
```

---

## 3. 功能变更记录

### 2026-02-10 v1.0.0 - 初始版本

**新增功能**:
- ✅ 支持多 RSS 源配置（YAML 文件）
- ✅ TAG 标识区分不同 RSS 源
- ✅ 新文章检测 API（支持 tag 参数）
- ✅ 按时间清理缓存（days 参数）
- ✅ Markdown 格式输出（适合钉钉）
- ✅ SQLite 持久化存储
- ✅ Docker 容器化部署
- ✅ API Gateway 集成

**用户体验变化**:
- 用户可以同时监控多个公众号
- 每个公众号独立管理缓存
- 支持定期清理旧数据

---

## 4. 非功能需求

### 4.1 性能要求

- API 响应时间: < 2 秒（取决于 RSS 源响应速度）
- 并发支持: 支持多个 n8n 工作流同时调用

### 4.2 可用性要求

- 服务可用性: 99%+
- 健康检查接口: 必须提供
- 优雅降级: RSS 源不可用时返回错误信息

### 4.3 可维护性要求

- 配置文件: YAML 格式，易于编辑
- 日志输出: 输出到 stdout（Docker 标准）
- 数据存储: SQLite，易于备份和迁移

### 4.4 扩展性要求

- 新增 RSS 源: 只需修改配置文件
- API 版本管理: 遵循 RESTful 规范

---

## 5. 用户使用流程

### 5.1 初次使用

1. **配置 RSS 源**
   - 编辑 `rss_sources.yaml`
   - 添加公众号名称、RSS 链接、TAG 标识

2. **启动服务**
   ```bash
   cd docker
   docker-compose up -d --build
   ```

3. **验证服务**
   ```bash
   curl http://localhost:8020/health
   curl http://localhost:8020/api/rss/sources
   ```

4. **测试检测**
   ```bash
   curl "http://localhost:8020/api/rss/check?tag=touzi"
   ```

### 5.2 n8n 集成

1. **创建定时触发器**
   - Cron: `45 2 * * *`（每天 2:45）

2. **添加 HTTP Request 节点**
   - Method: `GET`
   - URL: `http://api-gateway:8010/api/rss-notice/check?tag=touzi`

3. **添加判断节点**
   - 条件: `{{$json.new_count > 0}}`

4. **添加钉钉节点**
   - 使用返回的 markdown 字段发送消息

### 5.3 日常维护

1. **新增 RSS 源**
   - 编辑 `rss_sources.yaml`
   - 重启服务：`docker-compose restart`

2. **清理旧数据**
   ```bash
   # 清除最近 30 天的记录
   curl -X POST "http://localhost:8020/api/rss/refresh?days=30"
   ```

3. **重新同步某个源**
   ```bash
   # 清除该源缓存
   curl -X POST "http://localhost:8020/api/rss/refresh?tag=touzi"
   # 再次检查将获取所有文章
   curl "http://localhost:8020/api/rss/check?tag=touzi"
   ```

---

## 6. 限制与约束

### 6.1 技术限制

- RSS 源必须可公开访问
- RSS 格式需符合 RSS 2.0 或 Atom 标准
- 文章去重基于文章链接的 MD5 值

### 6.2 使用限制

- 不支持 RSS 源的实时推送（轮询模式）
- 不支持全文搜索功能
- 不支持文章内容抓取（仅元数据）

---

## 7. 未来规划

### 7.1 短期计划（v1.1.0）

- [ ] 支持 RSS 源的启用/禁用
- [ ] 增加文章过滤规则（关键词过滤）
- [ ] 支持 Webhook 通知方式

### 7.2 中期计划（v1.2.0）

- [ ] Web UI 管理界面
- [ ] 支持更多消息平台（企业微信、飞书）
- [ ] 文章分类和标签功能

### 7.3 长期计划（v2.0.0）

- [ ] 分布式部署支持
- [ ] 数据分析和统计
- [ ] 机器学习推荐
