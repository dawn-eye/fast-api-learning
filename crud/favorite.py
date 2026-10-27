from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.favorite import Favorite


#检查收藏状态： 当前用户 是否收藏了该新闻
async def is_news_favorite(
    db: AsyncSession,
    user_id: int,
    news_id: int
):
   query =  select(Favorite).where(Favorite.news_id == news_id, Favorite.user_id == user_id)
   result = await db.execute(query)
   #是否有收藏记录
   return result.scalar_one_or_none()  is not None