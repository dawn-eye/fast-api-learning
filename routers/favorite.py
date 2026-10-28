from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from config.db_config import get_db
from models.users import User
from schemas.favorite import FavoriteCheckresponse, FavoriteAddResponse
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