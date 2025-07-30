from __future__ import annotations

import colorlog
from scrapy.crawler import Crawler
from scrapy.settings import Settings
from typing_extensions import Self

from .default_format import LOG_DEFAULT_FORMAT, LOG_DEFAULT_DATEFORMAT, LOG_DEFAULT_LEVEL_COLORS, LOG_DEFAULT_MESSAGE_COLORS, LOG_DEFAULT_ASCTIME_COLORS, LOG_DEFAULT_NAME_COLORS


class ColoredFormatter(colorlog.ColoredFormatter):
    @classmethod
    def from_crawler(cls, crawler: Crawler) -> Self:
        return cls.from_settings(crawler.settings)

    @classmethod
    def from_settings(cls, settings: Settings) -> Self:

        # 获取配置或使用默认值
        message_colors = settings.getdict("LOG_DEFAULT_MESSAGE_COLORS", LOG_DEFAULT_MESSAGE_COLORS)
        asctime_colors = settings.getdict("LOG_DEFAULT_ASCTIME_COLORS", LOG_DEFAULT_ASCTIME_COLORS)
        name_colors = settings.getdict("LOG_DEFAULT_NAME_COLORS", LOG_DEFAULT_NAME_COLORS)

        # # 配置二级颜色
        secondary_log_colors = {
            'asctime': asctime_colors,
            'name': name_colors,
            'message': message_colors,
        }

        return cls(
            fmt=settings.get("LOG_DEFAULT_FORMAT", LOG_DEFAULT_FORMAT),
            datefmt=settings.get("LOG_DEFAULT_DATEFORMAT", LOG_DEFAULT_DATEFORMAT),
            log_colors=settings.getdict("LOG_DEFAULT_LEVEL_COLORS", LOG_DEFAULT_LEVEL_COLORS),
            secondary_log_colors=secondary_log_colors,
            reset=settings.getbool("LOG_RESET", True),
            no_color=settings.getbool("LOG_NO_COLOR", False),
            force_color=settings.getbool("LOG_FORCE_COLOR", False),
        )
