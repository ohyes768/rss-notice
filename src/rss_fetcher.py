"""
RSS拉取模块
负责解析RSS源并提取文章信息
"""
import feedparser
import hashlib
import logging
from typing import List, Dict
from datetime import datetime

from storage import Storage

logger = logging.getLogger(__name__)


class RSSFetcher:
    """RSS订阅源拉取器"""

    def __init__(self, storage: Storage):
        self.storage = storage

    def _generate_article_id(self, article_link: str) -> str:
        """生成文章唯一ID(MD5)"""
        return hashlib.md5(article_link.encode('utf-8')).hexdigest()

    def _generate_markdown(self, title: str, link: str, published: datetime, feed_title: str) -> str:
        """生成文章的Markdown格式信息"""
        published_time = published.strftime('%Y-%m-%d %H:%M') if published else '未知'

        markdown = f"""📰 公众号「{feed_title}」今日更新

### {title}

📅 发布：{published_time}
🔗 链接：{link}

---
"""
        return markdown

    def fetch_new_articles(self, rss_url: str, tag: str) -> Dict:
        """拉取新文章（过滤已处理的）"""
        logger.info(f"开始拉取RSS: {rss_url} (tag: {tag})")

        try:
            # 解析RSS
            feed = feedparser.parse(rss_url)

            if feed.bozo:
                logger.warning(f"RSS解析可能有误: {feed.bozo_exception}")

            feed_title = feed.feed.get('title', 'Unknown RSS')

            # 解析文章
            all_articles = []
            for entry in feed.entries:
                try:
                    article_id = self._generate_article_id(entry.link)

                    # 解析发布时间
                    published = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        published = datetime(*entry.published_parsed[:6])

                    # 生成Markdown
                    markdown = self._generate_markdown(
                        title=entry.get('title', 'Untitled'),
                        link=entry.link,
                        published=published,
                        feed_title=feed_title
                    )

                    article = {
                        'id': article_id,
                        'title': entry.get('title', 'Untitled'),
                        'link': entry.link,
                        'published': published.isoformat() if published else None,
                        'author': entry.get('author'),
                        'markdown': markdown
                    }
                    all_articles.append(article)
                except Exception as e:
                    logger.warning(f"解析文章失败: {e}, 跳过")
                    continue

            logger.info(f"解析到 {len(all_articles)} 篇文章")

            # 过滤新文章（按tag）
            new_articles = [
                article for article in all_articles
                if not self.storage.is_article_processed(article['id'], tag)
            ]

            logger.info(f"其中 {len(new_articles)} 篇为新文章 (tag: {tag})")

            return {
                'tag': tag,
                'feed_title': feed_title,
                'new_articles': new_articles
            }

        except Exception as e:
            logger.error(f"拉取RSS失败: {e}", exc_info=True)
            raise
