import time
import base64
import json
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from typing import Optional

from code_exec.serivce.code_dispose import dispose
from code_exec.model.model import Item
from code_exec.model import model
from granian import Granian

app = FastAPI()


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    """统一处理参数验证错误"""
    request_body = await get_request_body(request)
    print(f"Invalid Request Parameters: {request_body}")
    print(f"Validation Error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content=model.res_failed(f"参数验证失败: {exc.errors()}")
    )


async def get_request_body(request: Request) -> dict:
    """获取请求体内容，支持JSON和表单数据"""
    try:
        if request.method == "POST":
            content_type = request.headers.get("content-type", "")
            if "application/json" in content_type:
                return await request.json()
            elif "form" in content_type:
                form_data = await request.form()
                return {k: v for k, v in form_data.items()}
        return dict(request.query_params)
    except Exception as e:
        return {"error": f"读取请求体失败: {str(e)}"}


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """请求日志中间件，记录所有请求信息"""
    request_body = await get_request_body(request)
    print(f"REQUEST {request.method} {request.url.path} => {json.dumps(request_body, default=str)}")

    response = await call_next(request)
    return response


@app.get("/")
@app.post("/")
def default():
    return "code exec"


@app.post("/api/exec")
def code_exec(item: Optional[Item] = None, request: Request = None):
    """代码执行接口，支持两种参数接收方式"""
    begin = time.time_ns()

    try:
        # 优先使用解析后的模型数据
        if item is not None:
            processed_item = item.dict()
        else:
            # 若模型解析失败，直接处理原始请求数据
            processed_item = {"raw_data": get_request_body(request)}

        print(f"Processed Item: {processed_item}")

        # 提取代码逻辑
        code = None
        if item:
            code = item.code
            if item.base64_code:
                decoded_bytes = base64.b64decode(item.base64_code)
                code = decoded_bytes.decode('utf-8')
                print(f"Decoded code from base64_code: {code[:100]}...")  # 避免打印过长代码

        if not code:
            raise HTTPException(status_code=400, detail="代码不能为空")

        # 执行代码处理
        ret = dispose(item.language if item else "python", item.inputs if item else [], code)

    except HTTPException as e:
        print(f"HTTP Error: {e.detail}")
        return model.res_failed(e.detail)
    except Exception as e:
        print(f"Unexpected Error: {str(e)}")
        return model.res_failed(f"执行失败: {str(e)}")
    finally:
        print(f"Request handled in {(time.time_ns() - begin) / 1e6:.2f} ms")

    return model.res_success(ret)


def run():
    # uvicorn.run('code_exec.controller.api:app', host="0.0.0.0", port=8080)
    server = Granian(
        "code_exec.controller.api:app",
        address="0.0.0.0",
        port=8080,
        interface="asgi")
    server.serve()

