"""
공통 예외 클래스 정의
"""
import sys
import traceback
import json
from typing import Union

class OsBaseException(Exception):
    def __init__(self, messageId: str, code: Union[str, Exception] = "UNKNOWN_ERROR", status_code: int = 500):
        self.messageId = messageId
        self.status_code = status_code
        
        # code가 Exception 객체인 경우 상세한 오류 정보 수집
        if isinstance(code, Exception):
            error_details = {
                "exception_type": type(code).__name__,
                "exception_message": str(code),
                "exception_args": code.args,
                "file_name": sys.exc_info()[2].tb_frame.f_code.co_filename,
                "line_number": sys.exc_info()[2].tb_lineno,
                "function_name": sys.exc_info()[2].tb_frame.f_code.co_name,
                "traceback": traceback.format_exc()
            }
            # 상세 정보를 JSON 형태로 code에 포함
            self.code = json.dumps(error_details, ensure_ascii=False, indent=2)
        else:
            self.code = code
            
        super().__init__(messageId)

class OsValidationException(OsBaseException):
    def __init__(self, messageId: str = "backend.message.validationException", code: Union[str, Exception] = "VALIDATION_ERROR"):
        super().__init__(messageId=messageId, code=code, status_code=500)

class OsNotFoundException(OsBaseException):
    def __init__(self, messageId: str = "backend.message.notFoundException", code: Union[str, Exception] = "NOT_FOUND"):
        super().__init__(messageId=messageId, code=code, status_code=500)
