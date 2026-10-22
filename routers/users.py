from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio.session import AsyncSession
from starlette import status

from crud import users
from models.users import User
from schemas.users import UserRequest, UserInfoResponse, UserAuthResponse, UserUpdateRequest, UserChangePasswordRequest
from config.db_config import get_db
from utils.auth import get_current_user
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

@router.post("/login")
async def login_user(user_data:UserRequest,db: AsyncSession = Depends(get_db)):
   #登录逻辑： 验证用户是否存在 -> 验证密码是否正确 -> 生成 token -> 响应结果
   user = await users.authenticate_user(user_data.username,user_data.password,db)
   if not user:
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
   token = await users.create_token(db,user.id)
   response_data = UserAuthResponse(token=token,user_info=user)
   return succsess_response(message="登录成功",data = response_data)

#查Token查用户 -> 封装crud -> 功能整合成一个工具函数 ->路由导入使用:依赖注入
@router.get("/info")
async def get_user_info(user:User = Depends(get_current_user)):
   return succsess_response(message="用户信息获取成功",data = UserInfoResponse.model_validate(user) )

#修改用户信息：验证Token -> 更新(用户输入数据 put提交->请求体参数->定义Pydantic模型类) -> 响应结果
#参数:用户输入的 + 验证Token的 + db(调用更新的方法)
@router.put("/update")
async def update_user_info(
        user_data:UserUpdateRequest,
        user:User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
   user =  await users.update_user(user_data,user.username,db)
   return succsess_response(message="用户信息更新成功" ,data=UserInfoResponse.model_validate(user))

@router.put("/password")
async def update_password(
        passwprd_data:UserChangePasswordRequest,
        user:User = Depends(get_current_user),
        db : AsyncSession = Depends(get_db)):
   res_change_pwd = await users.change_password(passwprd_data.old_password,passwprd_data.new_password,user,db)
   if not res_change_pwd:
      raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="密码修改失败，请稍后再试")
   return succsess_response(message="密码修改成功")

