# 整合 根据 Token 查询用户, 返回用户
from fastapi import Header, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_config import get_db
from crud import users


async def get_current_user(
        authorization: str = Header(..., alias="Authorization"),
        db: AsyncSession = Depends(get_db)
):
    # 兼容多种写法：Bearer xxx / bearer xxx / 直接 token / 首尾多余空格
    token = authorization.strip()
    if token.lower().startswith("bearer "):
        token = token[len("bearer "):].strip()

    user = await users.get_user_by_token(token, db)

    if not user:
        raise HTTPException(status_code=401, detail="无效的令牌或已经过期的令牌")

    return user

