from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from models.news import Category,News
from models.users import User
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
