from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine

# 数据库URL
ASYNC_DATABASE_URL = "mysql+aiomysql://root:lbxx15888@localhost:3306/news_app?charset=utf8mb4"

# 创建异步引擎
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=True,          # 可选：输出SQL日志
    pool_size=10,       # 设置连接池中保持的持久连接数
    max_overflow=20,    # 设置连接池中最多可以创建的额外连接数
)

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# 依赖项，用于获取数据库会话
async def get_db():
    """
    FastAPI 依赖注入：每个请求都会分配一个独立的数据库会话，
    请求结束后自动关闭会话。
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session          # 把 session 交给路由函数使用
            await session.commit() # 如果路由没报错，自动提交事务
        except Exception:
            await session.rollback() # 如果路由里报错了，回滚事务
            raise                    # 把异常抛出去，让全局异常处理器接管
        finally:
            await session.close()    # 无论如何，最后关闭会话（其实 async with 会自动关，写出来更清晰）

