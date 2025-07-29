from typing import Any, Dict, List, Union
from rest_framework.views import exception_handler
from rest_framework.response import Response
from osshared.response.responseBuilder import ResponseBuilder
from osshared.exception.exception import OsBaseException
import traceback
import json


def globalExceptionHandler(exc: Exception, context: Dict[str, Any]) -> Response:
    print("🔥 예외 진입 확인:", type(exc), str(exc)) 

    # 커스텀 예외 처리
    if isinstance(exc, OsBaseException):
        # code가 JSON 형태인지 확인하고 파싱
        error_code = exc.code
        error_details = {}
        
        try:
            # code가 JSON 형태인 경우 파싱
            if isinstance(exc.code, str) and exc.code.strip().startswith('{'):
                error_details = json.loads(exc.code)
                error_code = error_details.get("exception_type", "CUSTOM_ERROR")
        except (json.JSONDecodeError, AttributeError):
            # JSON 파싱 실패 시 기존 code 사용
            error_code = exc.code
            error_details = {}
        
        return Response(ResponseBuilder.buildExceptionDict(
            messageId=exc.messageId,
            errors=[{
                "code": error_code,
                "messageId": exc.messageId,
                "details": error_details if error_details else None
            }]
        ), status=getattr(exc, 'status_code', 500))  # status_code가 없으면 500 사용

    # 기본 DRF 예외 핸들링으로 fallback
    response = exception_handler(exc, context)

    if response is not None:
        return Response(ResponseBuilder.buildExceptionDict(
            messageId="Unhandled error occurred",
            errors=[{
                "code": "UNHANDLED",
                "message": str(exc),
                "trace": traceback.format_exc()
            }]
        ), status=getattr(exc, 'status_code', 500))

    # 알 수 없는 에러
    return Response(ResponseBuilder.buildExceptionDict(
        messageId="Internal Server Error",
        errors=[{
            "code": "INTERNAL_ERROR",
            "message": str(exc),
            "trace": traceback.format_exc()
        }]
    ), status=500)  # 알 수 없는 에러는 항상 500
