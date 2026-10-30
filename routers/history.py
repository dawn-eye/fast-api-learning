from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_config import get_db
from crud import history
from models.users import User
from schemas.history import HistoryAddRequest, HistoryItemResponse, HistoryListResponse
from utils.auth import get_current_user
from utils.response import success_response

router = APIRouter(prefix="/api/history",tags=["history"])

@router.post("/add")
async def add_history(
        data: HistoryAddRequest,   #无默认值参数还要放在前面
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user)

):
    result = await history.add_history(db, user.id, data.news_id)
    return success_response(message="添加成功",data = HistoryItemResponse.model_validate(result))

@router.get("/list")
async def get_history_list(
        page :int = Query(1,ge = 1),
        page_size : int =Query(10,ge = 1,le = 10,alias="pageSize"),
        user: User = Depends(get_current_user),
        db:AsyncSession = Depends(get_db)
):
    rows, total = await history.get_history_list(db, user.id, page, page_size)
    history_list = [{
        **news.__dict__,
        "viewTime": view_time
    }for news,view_time in rows]
    has_more = total > page * page_size

    data = HistoryListResponse(list=history_list,total=total,hasMore=has_more)
    return success_response(message="获取浏览记录成功" ,data = data)

