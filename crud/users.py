import uuid
from datetime import datetime, timedelta

from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from models.news import Category,News
from models.users import User, UserToken
from schemas.users import UserRequest
from utils import security

#根据用户名查询数据库
async def get_user_by_username(username: str,db:AsyncSession):
    query = select(User).where(username == User.username)
    result = await db.execute(query)
    return result.scalar_one_or_none()

#创建用户
async def create_user(user_data:UserRequest, db: AsyncSession):
    #先密码加密 -> add
    secu = security.get_hash_password(user_data.password)
    user = User(username=user_data.username, password=secu)
    db.add(user)
    await db.commit()
    await db.refresh(user) #从数据库读回最新的 user
    return user


#生成token
async def create_token(db:AsyncSession,user_id:int):
    # 生成 Token + 设置过期时间->查询数据库当前用户是否有Token ->有：更新; 没有：添加
    token = str(uuid.uuid4())
    expires_at = datetime.now() + timedelta(days=7)
    query = select(UserToken).where(UserToken.user_id == user_id)
    result = await db.execute(query)
    user_token = result.scalar_one_or_none()

    if user_token:
        UserToken.token = token
        UserToken.expires_at = expires_at
    else:
        user_token = UserToken(user_id=user_id, token=token, expires_at=expires_at)
        db.add(user_token)
    await db.commit()

    return token
