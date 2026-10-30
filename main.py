from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles
from routers import news, users, favorite, history
from utils.exception_handlers import register_exception_handlers

# 静态资源目录：swagger-ui 的 js/css/图标都放在这里，不再依赖国外 CDN
# 用 Path(__file__).parent 而不是相对路径，这样从任何目录启动 uvicorn 都能找到
STATIC_DIR = Path(__file__).parent / "static"

# docs_url=None / redoc_url=None：先关掉 FastAPI 自带的文档页
# 自带文档页引用的 js/css 都在 cdn.jsdelivr.net 上，国内经常连不上，会白屏
# 所以下面用 get_swagger_ui_html 自己生成一个指向本地文件的文档页
app = FastAPI(docs_url=None, redoc_url=None)

#注册异常处理器
register_exception_handlers(app)

#后续上线可以限制来源
#origins = []

#同源的三个条件是什么： 协议，域名，端口
#解决跨域问题：全局配置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],     #允许的源，开发阶段允许所有源，生产环境需要指定源
    allow_credentials=True,  #允许携带cookie
    allow_methods=["*"],     #允许的请求方法
    allow_headers=["*"]      #允许的请求头
)

# 把本地 static 目录挂载到 /static 路径下
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """接口文档页：js/css/图标全部指向本地 /static 文件，断网也能用"""
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
        swagger_favicon_url="/static/favicon.png",
    )


@app.get("/")
async def root():
    return {"message": "Hello World"}

#挂载路由/注册路由
app.include_router(news.router)
app.include_router(users.router)
app.include_router(favorite.router)
app.include_router(history.router)
