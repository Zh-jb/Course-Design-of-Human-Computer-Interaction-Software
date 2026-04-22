from  fastapi import FastAPI
from datetime import datetime
app = FastAPI()
@app.get("/")
def root():
    return {
        "message": "欢迎访问Courseqa课程网页"
        }
@app.get("/get")
def get():
    return {
        "项目名称":"智慧课程问答系统Courseqa",
        "项目第一阶段":"完成API的基础调用",
        }
@app.get("/health")
def health():
    return{
        "API状态":"API已成功调用并正常运行",
    }
@app.get("/info")
def info():
    return {
  "project": "courseqa",
  "lesson": "第8次课",
  "status": "running"
}
@app.get("/time")
def time():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {
        "current_time": now
    }
'''
@app.get("/hello/{name}")
def hello(name:str):
    return{
        "Hello!":name
    }
'''

@app.get("/hello")
def hello(name:str):
    return{
        "Hello!":name
    }
'''
@app.get("/add/{a}/{b}")
def add(a:int,b:int):
    return{
        f"{a}+{b}=": a+b
    }
'''
@app.get("/add")
def add(a:int,b:int):
    return{
        f"{a}+{b}=": a+b
    }