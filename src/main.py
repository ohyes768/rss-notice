"""
FastAPI应用入口
提供RSS订阅监控的RESTful API
"""
from fastapi import FastAPI, HTTPException, Query
from typing import Optional

from config import Config
from storage import Storage
from rss_fetcher import RSSFetcher
from logger import setup_logger
from models import HealthResponse, RSSCheckResponse, Article

# 初始化
setup_logger()
config = Config()
storage = Storage(config.db_path)
fetcher = RSSFetcher(storage)

app = FastAPI(
    title="RSS Notice Service",
    description="RSS订阅监控服务",
    version="1.0.0"
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查端点（必需）"""
    return HealthResponse(
        status="healthy",
        service="rss-notice"
    )


@app.get("/api/rss/check", response_model=RSSCheckResponse)
async def check_new_articles(tag: str = Query(..., description="RSS源的TAG标识")):
    """
    检查新文章
    由n8n通过API Gateway调用

    参数:
    - tag: RSS源的TAG标识（必需），如: touzi
    """
    try:
        # 获取RSS源配置
        rss_url = config.get_rss_url(tag)
        if not rss_url:
            raise HTTPException(
                status_code=404,
                detail=f"未找到tag为'{tag}'的RSS源，请检查rss_sources.yaml配置"
            )

        # 拉取新文章
        result = fetcher.fetch_new_articles(rss_url, tag)
        new_articles = result['new_articles']

        # 保存到数据库
        storage.save_articles(new_articles, tag)

        # 转换为Article模型
        articles = [Article(**article) for article in new_articles]

        # 构造响应
        response = RSSCheckResponse(
            feed_title=result['feed_title'],
            feed_url=rss_url,
            feed_updated=result['feed_updated'],
            new_count=len(new_articles),
            articles=articles
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检查失败: {str(e)}")


@app.post("/api/rss/refresh")
async def refresh_articles(
    tag: Optional[str] = Query(None, description="RSS源的TAG标识（可选），不传则清除所有"),
    days: Optional[int] = Query(None, description="清除最近N天的记录（可选），如7、30")
):
    """
    清除缓存
    清除已处理文章的记录

    参数:
    - tag: RSS源的TAG标识（可选）
      - 指定tag: 只清除该tag的文章
      - 不传tag: 清除所有文章
    - days: 清除最近N天的记录（可选）
      - 不传days: 清除全部记录
      - days=7: 清除最近7天的记录
      - days=30: 清除最近30天的记录

    优先级: days参数优先，即如果指定days，则按时间清除
    """
    try:
        if days is not None:
            # 按时间清除
            if days <= 0:
                raise HTTPException(status_code=400, detail="days参数必须大于0")

            count = storage.clear_articles_by_days(days, tag)

            if tag:
                message = f"已清除tag为'{tag}'的最近{days}天的 {count} 篇文章记录"
            else:
                message = f"已清除最近{days}天的 {count} 篇文章记录"

            return {
                "status": "success",
                "message": message,
                "cleared_count": count,
                "tag": tag,
                "days": days
            }
        else:
            # 清除全部
            count = storage.clear_all_articles(tag)

            if tag:
                message = f"已清除tag为'{tag}'的 {count} 篇文章记录"
            else:
                message = f"已清除所有 {count} 篇文章记录"

            return {
                "status": "success",
                "message": message,
                "cleared_count": count,
                "tag": tag
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清除失败: {str(e)}")


@app.get("/api/rss/sources")
async def list_sources():
    """
    列出所有配置的RSS源
    """
    sources = config.get_all_rss_sources()
    return {
        "count": len(sources),
        "sources": [
            {
                "tag": tag,
                "name": source['name'],
                "url": source['url']
            }
            for tag, source in sources.items()
        ]
    }
