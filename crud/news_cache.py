from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from models.news import Category,News
from cache.news_cache import set_cached_categories, get_cached_categories, get_cached_news_list, set_cached_news_list
from schemas.base import NewsItemBase


async  def get_categories(db:AsyncSession,skip:int = 0, limit:int = 100):
    #先尝试从缓存中获取数据
    cached_categories = await get_cached_categories()
    if cached_categories:
        return cached_categories
    #如果缓存中没有数据，则从数据库中获取数据

    stmt = select(Category).offset(skip).limit(limit)
    result = await db.execute(stmt)
    categories = result.scalars().all()  #ORM对象列表

    # 写入缓存
    if categories:
        categories = jsonable_encoder(categories)
        await set_cached_categories(categories)

    # 返回数据
    return categories

async def get_news_list_by_category(db:AsyncSession, category_id:int, skip:int = 0, limit:int = 10):
    #先尝试从缓存中获取新闻列表
    # 跳过的数量skip  = (页码-1)*每页数量 ->页码 = 跳过的数量//每页数量 + 1
    page = skip//limit+1
    cache_list = await get_cached_news_list(category_id,page,limit)
    if cache_list:
        # return cache_list #要的是orm对象 但是这里面返回的是列表
        return [News(**item) for item in cache_list]


    #查询的是指定分类下的所有新闻
    stmt = select(News).where(News.category_id == category_id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    news_list =  result.scalars().all()

    #写入缓存
    if news_list:
        #先把 ORM 数据 转换 字典才能写入缓存
        #ORM 转换成 Pydantic，再转为字典
        #by_alias = False 不适用别名,保存 Python 风格,因为 Redis 数据是给后端用的
        news_data =[NewsItemBase.model_validate(item).model_dump(mode ="json",by_alias = False) for item in news_list]
        await set_cached_news_list(category_id,page,limit,news_data)
    return news_list

async def get_news_count(db:AsyncSession,category_id:int):
    stmt = select(func.count(News.id)).where(News.category_id == category_id)
    result = await db.execute(stmt)
    return result.scalar_one()#只能有一个结果，否则报错

#返回某单个新闻，并判断新闻是否存在
async def get_news_detail(db:AsyncSession, news_id:int):
    stmt = select(News).where(News.id == news_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def increase_news_views(db:AsyncSession,news_id:int):
    stmt = update(News).where(News.id == news_id).values(views = News.views + 1)
    result = await db.execute(stmt)
    #await db.commit() #提交到数据库

    #更新 ->检查数据库是否真的命中了数据 ->命中了返回True
    return result.rowcount > 0


async def get_related_news(db:AsyncSession,news_id,category_id, limit:int = 5):
    stmt = select(News).where(
        News.category_id == category_id,
        News.id != news_id
    ).order_by(
        News.views.desc(), #按照播放量降序
        News.publish_time.desc() #按照创建时间降序
    ).limit(limit)
    result = await db.execute(stmt)
    # return result.scalars().all()
    related_news = result.scalars().all()
    #列表推导式 推导出新闻的核心数据,然后再return
    return [{
        "id": news_detail.id,
    "title": news_detail.title,
    #"content": news_detail.content,   每次传都传内容的话，传输体量就会变大
    "image": news_detail.image,
    "author": news_detail.author,
    "publishTime": news_detail.publish_time,
    "categoryId": news_detail.category_id,
    "views": news_detail.views,} for news_detail in related_news]
