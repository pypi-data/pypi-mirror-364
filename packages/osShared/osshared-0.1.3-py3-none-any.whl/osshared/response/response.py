"""
API Response DTO 정의
"""
from typing import Generic, TypeVar, Optional, Any
from osshared.response.enum import enumResponseStatus
from pydantic import BaseModel
from datetime import datetime

class SampleResponse:
    def __init__(self, messageId: str):
        self.messageId = messageId


T = TypeVar('T')
class ResponseBase(Generic[T], BaseModel):
    status: enumResponseStatus
    data: Optional[T] = None
    messageId: Optional[str] = None
    errors: Optional[Any] = None
    traceId: Optional[str] = None
    timestamp: str = datetime.now().isoformat()
