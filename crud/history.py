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

#获取浏览列表 --->获取用户的浏览列表  + 分页功能
async def get_history_list(
        db:AsyncSession,
        user_id:int,
        page:int = 1,
        page_size:int = 10
):
    #总量 + 浏览记录列表
    count_query = select(func.count()).where(History.user_id == user_id)
    result = await db.execute(count_query)
    total = result.scalar_one()

    #获取浏览列表 - 联表查询 join() + 收藏时间排序 + 分页
    """
    查询最后得到的东西
    [
      (新闻对象，收藏对象，收藏id)
    ]
    """

    query = (select(News, History.view_time.label("view_time"))
               .join(History,History.news_id == News.id)
               .where(History.user_id == user_id )
               .order_by(History.view_time.desc())
               .offset((page - 1) * page_size)
               .limit(page_size))

    result = await db.execute(query)
    rows = result.all()
    return rows,total



async def delete_history(
        db:AsyncSession,
        user_id:int,
        news_id:int
):
  stmt =  delete(History).where(History.user_id == user_id, History.news_id == news_id)
  result = await db.execute(stmt)
  return result.rowcount > 0