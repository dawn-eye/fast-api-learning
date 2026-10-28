from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from config.db_config import get_db
from models.users import User
from schemas.favorite import FavoriteCheckresponse, FavoriteAddResponse, FavoriteListResponse
from utils.auth import get_current_user
from utils.response import success_response
from crud import favorite

router = APIRouter(prefix="/api/favorite",tags=["favorite"])
@router.get("/check")
async def check_favorite(
        new_id:int = Query(... ,alias = "newsId"),
        user:User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """
    检查新闻的收藏状态
    news_id:新闻id
    return :收藏状态
    """
    is_favorited = await favorite.is_news_favorite(db, user.id, new_id)
    return success_response(message="查看收藏状态成功",data = FavoriteCheckresponse(isFavorite = is_favorited))

@router.post("/add")
async def add_favorite(
        data: FavoriteAddResponse,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    result = await favorite.add_news_favorite(db, user.id, data.news_id)
    return success_response(message="添加收藏成功",data= result)

@router.delete("/remove")
async def remove_favorite(
        new_id:int = Query(... ,alias = "newsId"),
        user:User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    result = await favorite.remove_news_favorite(db, user.id, new_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="新闻不存在")
    return success_response(message="删除收藏成功")

@router.get("/list")
async def get_favorite_list(
        user:User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
        page: int =Query(1,ge=1),
        page_size: int = Query(10,ge=1,le=100,alias="pageSize")
):
    rows,total= await favorite.get_favorite_list(db, user.id, page, page_size)
    favorite_list = [{
        **news.__dict__,
        "favoriteTime": favorite_time,
        "favoriteId": favorite_id
    }for news, favorite_time, favorite_id in rows]
    has_more = total > page * page_size

    data = FavoriteListResponse(list =favorite_list,total= total,hasMore=has_more)
    return success_response(message="获取收藏列表成功",data = data)
