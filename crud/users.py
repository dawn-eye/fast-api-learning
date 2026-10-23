import uuid
from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from models.news import Category,News
from models.users import User, UserToken
from schemas.users import UserRequest, UserUpdateRequest
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
        user_token.token = token
        user_token.expires_at = expires_at
    else:
        user_token = UserToken(user_id=user_id, token=token, expires_at=expires_at)
        db.add(user_token)
    await db.commit()

    return token


#用户验证
async def authenticate_user(username: str, password: str, db: AsyncSession):
    user = await get_user_by_username(username,db)
    if not user:
        return None
    if not security.verify_password(password, user.password):
        return None
    return user

#根据Token查询用户:验证 Token ->查询用户
async def get_user_by_token(token: str, db: AsyncSession):
    query = select(UserToken).where(UserToken.token == token)
    result = await db.execute(query)
    db_token = result.scalar_one_or_none()

    if not db_token or db_token.expires_at < datetime.now():
        return None

    query = select(User).where(User.id == db_token.user_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()

#更新用户信息
async def update_user(user_data:UserUpdateRequest, username:str, db:AsyncSession):
    #update(User).where(User.username == username).values(字段=值,字段=值)
    #user_data 是一个Pydantic类型,得到字典->** 解包
    query = update(User).where(User.username == username).values(**user_data.model_dump(
        exclude_unset=True,
        exclude_none=True
    ))
    result = await db.execute(query)
    await db.commit()

    #检查更新
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="用户不存在")

    #获取一下更新后的用户

    updated_user = await get_user_by_username(username,db)
    return updated_user

#修改密码:验证旧密码 -> 新密码加密 -> 修改密码
async def change_password(old_password:str,new_password:str,user:User,db:AsyncSession):
    if not security.verify_password(old_password,user.password):
        return False
    hashed_new_pwd = security.get_hash_password(new_password)
    user.password = hashed_new_pwd
    #更新:由SQLAlchemy 真正接管这个User对象,确保可以 commit
    #规避 session 过期或关闭导致的不能提交的问题
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return True
