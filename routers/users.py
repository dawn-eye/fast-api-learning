from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio.session import AsyncSession
from starlette import status

from crud import users
from schemas.users import UserRequest, UserInfoResponse,UserAuthResponse
from config.db_config import get_db
from utils.response import succsess_response

router = APIRouter(prefix="/api/user", tags=["users"])

@router.post("/register")
async def register(user_data:UserRequest , db: AsyncSession = Depends(get_db)): #用户信息和db
   #验证用户是否存在 --> 创建用户  --> 生成 token  --> 响应结果
   exiting_user = await users.get_user_by_username(user_data.username,db,)
   if exiting_user:
       raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户已存在")
   user = await users.create_user(user_data,db)

   token = await users.create_token(db,user.id)
   # return {
   #      "code": 200,
   #      "message": "注册成功",
   #      "data": {
   #          "token": token,
   #          "userInfo": {
   #              "id": user.id,
   #              "username":user_data.username,
   #              "bio": user.bio,
   #              "avatar": user.avatar,
   #          }
   #      }
   #  }
   response_data =UserAuthResponse(token=token,user_info=user)
   return succsess_response(message="注册成功",data=response_data)