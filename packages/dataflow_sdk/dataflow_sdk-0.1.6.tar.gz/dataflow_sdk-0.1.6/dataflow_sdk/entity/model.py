from datetime import datetime
from enum import Enum
from typing import Optional, Any, Dict

from pydantic import BaseModel, Field


class SinkType(Enum):
    RAW = 0  # 日志、列表等原始数据
    ITEM = 1  # 清洗好的数据
    COMMENT = 2  # 评论数据
    PROFILE = 3  # 用户


class Record(BaseModel):
    parent_url: str = Field(default=None, description='parent url')
    sink_type: SinkType = Field(default=SinkType.ITEM, description='sink type')
    store_key: Optional[str] = Field(default='')
    crawl_time: Optional[str] = Field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    data: Optional[Any]
    metadata: Optional[Dict[str, Any]] = Field(default=None)
