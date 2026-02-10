"""
配置管理模块
从环境变量和YAML文件加载配置
"""
import os
import yaml
from pathlib import Path
from typing import Dict, Optional
from dotenv import load_dotenv


class Config:
    """配置管理器"""

    def __init__(self):
        env_path = Path(__file__).parent / ".env"
        load_dotenv(env_path)

        # 加载RSS源配置
        rss_config_path = Path(__file__).parent / "rss_sources.yaml"
        if rss_config_path.exists():
            with open(rss_config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
                self.rss_sources = config_data.get('sources', {})
        else:
            self.rss_sources = {}

    @property
    def db_path(self) -> str:
        return os.getenv("DB_PATH", "data/rss_notice.db")

    @property
    def log_level(self) -> str:
        return os.getenv("LOG_LEVEL", "INFO")

    def get_rss_source(self, tag: str) -> Optional[Dict]:
        """根据tag获取RSS源配置"""
        return self.rss_sources.get(tag)

    def get_all_rss_sources(self) -> Dict:
        """获取所有RSS源配置"""
        return self.rss_sources

    def get_rss_url(self, tag: str) -> Optional[str]:
        """根据tag获取RSS URL"""
        source = self.get_rss_source(tag)
        return source['url'] if source else None

    def get_rss_name(self, tag: str) -> Optional[str]:
        """根据tag获取公众号名称"""
        source = self.get_rss_source(tag)
        return source['name'] if source else None
