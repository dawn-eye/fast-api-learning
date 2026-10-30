from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from schemas.base import NewsItemBase


class HistoryAddRequest(BaseModel):

    """
    历史记录添加请求模型类
    继承自BaseModel，用于定义添加历史记录所需的请求数据结构
    """
    news_id: int = Field(...,alias = "newsId")  # 新闻ID字段，类型为整数，使用别名映射到"newsId"

    model_config = ConfigDict(
        populate_by_name=True,  # 配置允许通过名称(alias)来填充数据
    )

class HistoryItemResponse(BaseModel):
    """返回给前端的浏览记录"""
    id: int
    news_id: int = Field(..., alias="newsId")
    view_time: datetime = Field(..., alias="viewTime")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )

class HistoryNewsItemResponse(NewsItemBase):
    """返回给前端的浏览记录"""
    view_time: datetime = Field(..., alias="viewTime")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class HistoryListResponse(BaseModel):
    """返回给前端的浏览记录列表"""
    list:list[HistoryNewsItemResponse]
    total:int
    has_more:bool = Field(...,alias = "hasMore")

    model_config =  ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )