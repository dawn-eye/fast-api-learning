from fastapi import APIRouter,Depends,Query
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_config import get_db
from crud import news

#创建 APIRouter 实例
#prefix 路由前缀(API 接口规范文档)
#tags   分组---交互式文档结构更清晰
router = APIRouter(prefix="/api/news", tags=["news"])

#接口实现流程
#1. 模块化路由 -> API 接口规范文档
#2. 定义模型类 ->数据库表(数据库设计文档)
#3. 在crud 文件夹中创建文件,封装数据库的方法
#4. 在路由处理函数里面调用crud封装好的方法，响应结果
@router.get("/categories")
async def get_categories(skip :int = 0, limit :int = 100,db:AsyncSession = Depends(get_db)):
    # 先获取数据库里面新闻分类数据 -> 先定义模型类 -> 封装查询数据的方法
    categories = await news.get_categories(db,skip,limit)
    return  {
        "code":200,
        "message":"获取新闻分类成功",
        "data": categories
    }

@router.get("/list")
async def get_news_list_by_category(
        category_id: int = Query(..., alias="categoryId"),
        page: int = 1,
        page_size: int = Query(10, alias="pageSize", le=100),
        db: AsyncSession = Depends(get_db)):
    #查询的是指定分类下的所有新闻
    offset = (page - 1) * page_size
    news_list = await news.get_news_detail(db, category_id, offset, page_size)
    total = await news.get_news_count(db, category_id)
    # 跳过的+当前列表的数量是否小于总量<总量
    has_more = (offset + len(news_list)) < total
    return {
        "code": 200,
        "message": "获取新闻详情成功",
        "data": {
                    "list": news_list,
                    "total": total,
                    "hasMore": has_more
                }
    }
@router.get("/detail")
async def get_news_detail(
        category_id :int = Query(...,alias="categoryId"),
        page :int = 1,
        page_size :int = Query(10,alias="pageSize", le=100),
        db:AsyncSession = Depends(get_db)):
    #思路:处理分页规则->查询新闻列表->计算总量 -> 计算是否还有更多
    offset = (page-1)*page_size
    news_list = await news.get_news_detail(db,category_id,offset,page_size)
    total = await news.get_news_count(db,category_id)
    #跳过的+当前列表的数量是否小于总量<总量
    has_more = (offset+ len(news_list))< total
    return {
        "code":200,
        "message":"获取新闻详情成功",
        "data": {
            "list": news_list,
            "total":total,
            "hasMore":has_more
    }
}