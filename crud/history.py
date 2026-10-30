from datetime import datetime

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import func

from models.favorite import Favorite
from models.history import History
from models.news import News

#添加浏览记录 -->用户是否登录--->检查是否浏览过当前新闻--->浏览过则更新浏览时间--->未浏览过则添加浏览记录
async def add_history(
        db:AsyncSession,
        user_id:int,
        news_id:int
):
    query = select(History).where(
        History.user_id == user_id,
        History.news_id == news_id
    )
    result = await db.execute(query)
    history_record = result.scalar_one_or_none()

    if not history_record:
        history_record = History(user_id=user_id, news_id=news_id)
        db.add(history_record)
    else:
        history_record.view_time = datetime.now()
    await db.flush()
    await db.refresh(history_record)

    return history_record

