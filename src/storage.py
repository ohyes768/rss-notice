"""
SQLite持久化存储模块
用于记录已处理的文章，避免重复通知
"""
import sqlite3
import hashlib
from pathlib import Path
from typing import Set
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class Storage:
    """SQLite持久化存储"""

    def __init__(self, db_path: str = "data/rss_notice.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """初始化数据库表"""
        with sqlite3.connect(self.db_path) as conn:
            # 创建表（如果不存在）
            conn.execute("""
                CREATE TABLE IF NOT EXISTS articles (
                    id TEXT PRIMARY KEY,
                    tag TEXT NOT NULL,
                    title TEXT NOT NULL,
                    link TEXT NOT NULL,
                    published TEXT,
                    author TEXT,
                    created_at TEXT NOT NULL
                )
            """)
            conn.commit()

            # 检查并添加tag列（如果表已存在但没有tag列）
            cursor = conn.execute("PRAGMA table_info(articles)")
            columns = [row[1] for row in cursor.fetchall()]
            if 'tag' not in columns:
                logger.info("检测到旧版数据库，添加tag字段...")
                conn.execute("ALTER TABLE articles ADD COLUMN tag TEXT DEFAULT 'default'")
                conn.commit()

            logger.info(f"数据库初始化完成: {self.db_path}")

    def is_article_processed(self, article_id: str, tag: str) -> bool:
        """检查文章是否已处理（按tag区分）"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT 1 FROM articles WHERE id = ? AND tag = ? LIMIT 1",
                (article_id, tag)
            )
            return cursor.fetchone() is not None

    def save_articles(self, articles: list, tag: str) -> int:
        """保存文章到数据库，返回保存数量"""
        saved_count = 0
        now = datetime.now().isoformat()

        with sqlite3.connect(self.db_path) as conn:
            for article in articles:
                try:
                    conn.execute(
                        """
                        INSERT INTO articles
                        (id, tag, title, link, published, author, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            article['id'],
                            tag,
                            article['title'],
                            article['link'],
                            article.get('published'),
                            article.get('author'),
                            now
                        )
                    )
                    saved_count += 1
                except sqlite3.IntegrityError:
                    pass  # 文章已存在
            conn.commit()
            logger.info(f"保存了 {saved_count} 篇新文章 (tag: {tag})")
            return saved_count

    def clear_all_articles(self, tag: str = None) -> int:
        """清除文章记录，返回清除数量
        如果指定tag，只清除该tag的文章；否则清除所有
        """
        with sqlite3.connect(self.db_path) as conn:
            if tag:
                cursor = conn.execute("SELECT COUNT(*) FROM articles WHERE tag = ?", (tag,))
                count = cursor.fetchone()[0]
                conn.execute("DELETE FROM articles WHERE tag = ?", (tag,))
                logger.info(f"清除了 {count} 篇文章记录 (tag: {tag})")
            else:
                cursor = conn.execute("SELECT COUNT(*) FROM articles")
                count = cursor.fetchone()[0]
                conn.execute("DELETE FROM articles")
                logger.info(f"清除了 {count} 篇文章记录 (全部)")

            conn.commit()
            return count

    def clear_articles_by_days(self, days: int, tag: str = None) -> int:
        """按天数清除文章记录，返回清除数量

        参数:
        - days: 清除最近N天的文章（如7天、30天）
        - tag: 可选，指定tag则只清除该tag的文章

        示例:
        - days=7: 清除最近7天的文章
        - days=30: 清除最近30天的文章
        """
        from datetime import timedelta

        cutoff_time = (datetime.now() - timedelta(days=days)).isoformat()

        with sqlite3.connect(self.db_path) as conn:
            if tag:
                cursor = conn.execute(
                    "SELECT COUNT(*) FROM articles WHERE tag = ? AND created_at >= ?",
                    (tag, cutoff_time)
                )
                count = cursor.fetchone()[0]
                conn.execute(
                    "DELETE FROM articles WHERE tag = ? AND created_at >= ?",
                    (tag, cutoff_time)
                )
                logger.info(f"清除了 {count} 篇文章记录 (tag: {tag}, 最近{days}天)")
            else:
                cursor = conn.execute(
                    "SELECT COUNT(*) FROM articles WHERE created_at >= ?",
                    (cutoff_time,)
                )
                count = cursor.fetchone()[0]
                conn.execute(
                    "DELETE FROM articles WHERE created_at >= ?",
                    (cutoff_time,)
                )
                logger.info(f"清除了 {count} 篇文章记录 (最近{days}天)")

            conn.commit()
            return count
