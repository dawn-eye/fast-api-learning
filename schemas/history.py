from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

class HistoryAddRequest(BaseModel):
    news_id: int = Field(...,alias = "newsId")

    model_config = ConfigDict(
        populate_by_name=True,
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