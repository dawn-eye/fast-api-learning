from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import news, users

app = FastAPI()

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



@app.get("/")
async def root():
    return {"message": "Hello World"}

#挂载路由/注册路由
app.include_router(news.router)
app.include_router(users.router)