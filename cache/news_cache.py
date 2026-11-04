# 新闻相关的缓存方法:新闻分类的读取和写入
# key - value
from typing import Dict, List, Any, Optional

from config.cache_config import get_json_cache, set_cache

CATEGORIES_KET = "news:categories"
NEWS_LIST_PREFIX = "news_list:"


#获取新闻分类缓存
async def get_cached_categories():
    return await get_json_cache(CATEGORIES_KET)

#写入新闻分类缓存:缓存的数据，过期的时间
#分类,配置 7200,列表：600;详情：1800；验证码：120 --验证越稳定,缓存越持久
#避免所有的key同时过期引发缓存雪崩
async def set_cached_categories(data:List[Dict[str,Any]],expire:int = 7200):
    return await set_cache(CATEGORIES_KET,data,expire)


#写入缓存-新闻列表 key = news_list:分类id:页码: 每页数量 + 列表数据 + 过期时间
async def set_cached_news_list(category_id:Optional[int],page:int,size:int,news_list:List[Dict[str,Any]],expire:int = 1800):
    #掉用 封装的 Redis 的设置方法,存新闻列表到缓存
    category_part = category_id if category_id is not None else "all"
    key = f"{NEWS_LIST_PREFIX}{category_part}:{page}:{size}"
    await set_cache(key,news_list,expire)


#读取缓存-新闻列表
async def get_cached_news_list(category_id:Optional[int],page:int,size:int):
    category_part = category_id if category_id is not None else "all"
    key = f"{NEWS_LIST_PREFIX}{category_part}:{page}:{size}"
    return await get_json_cache(key)




