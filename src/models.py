"""
数据模型定义
使用Pydantic定义强类型数据结构
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional


class Article(BaseModel):
    """文章数据模型"""
    id: str = Field(..., description="文章唯一标识(MD5)")
    title: str = Field(..., description="文章标题")
    link: str = Field(..., description="文章链接")
    published: Optional[datetime] = Field(None, description="发布时间")
    author: Optional[str] = Field(None, description="作者")
    markdown: str = Field(..., description="Markdown格式的文章信息")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class RSSCheckResponse(BaseModel):
    """RSS检查响应"""
    feed_title: str = Field(..., description="订阅源标题")
    feed_url: str = Field(..., description="订阅源URL")
    check_time: datetime = Field(default_factory=datetime.now, description="检查时间")
    new_count: int = Field(..., description="新增文章数量")
    articles: List[Article] = Field(..., description="新增文章列表")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str = Field(..., description="健康状态")
    service: str = Field(..., description="服务名称")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")
