from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_config import get_db
from models.users import User
from schemas.favorite import FavoriteCheckresponse
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

