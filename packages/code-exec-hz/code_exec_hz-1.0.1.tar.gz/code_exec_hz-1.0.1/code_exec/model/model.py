import uuid
from typing import Optional, Dict, Any

from pydantic import BaseModel
from fastapi.responses import JSONResponse, Response


class Item(BaseModel):
    language: Optional[str] = None
    inputs: Dict[str, Any] = {}
    code: Optional[str] = None
    base64_code: Optional[str] = None


class LanguageType:
    PYTHON = 'python'
    SQL = 'sql'
    JAVASCRIPT = 'javascript'


def res_success(ret) -> Response:
    return JSONResponse(
        content={
            'status': 0,
            'msg': 'success',
            'result': ret,
            'trcid': str(uuid.uuid4())
        }
    )


def res_failed(msg) -> Response:
    return JSONResponse(
        content={
            'status': 0,
            'msg': msg,
            'result': {},
            'trcid': str(uuid.uuid4())
        }
    )
