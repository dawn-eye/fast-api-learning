from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from models.news import Category,News

async  def get_categories(db:AsyncSession,skip:int = 0, limit:int = 100):
    stmt = select(Category).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_news_detail(db:AsyncSession,category_id:int,skip:int = 0, limit:int = 10):
    #查询的是指定分类下的所有新闻
    stmt = select(News).where(News.category_id == category_id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_news_count(db:AsyncSession,category_id:int):
    stmt = select(func.count(News.id)).where(News.category_id == category_id)
    result = await db.execute(stmt)
    return result.scalar_one()#只能有一个结果，否则报错

#返回某单个新闻，并判断新闻是否存在
async def get_news_detail_isnull(db:AsyncSession,news_id:int):
    stmt = select(News).where(News.id == news_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def increase_news_views(db:AsyncSession,news_id:int):
    stmt = update(News).where(News.id == news_id).values(views = News.views + 1)
    result = await db.execute(stmt)
    await db.commit() #提交到数据库

    #更新 ->检查数据库是否真的命中了数据 ->命中了返回True
    return result.rowcount > 0


async def get_related_news(db:AsyncSession,news_id,category_id, limit:int = 5):
    stet = select(News).where(
        News.category_id == category_id,
        News.id != news_id
    ).order_by(
        News.views.desc(), #按照播放量降序
        News.publish_time.desc() #按照创建时间降序
    ).limit(limit)
    result = await db.execute(stet)
    return result.scalars().all()
