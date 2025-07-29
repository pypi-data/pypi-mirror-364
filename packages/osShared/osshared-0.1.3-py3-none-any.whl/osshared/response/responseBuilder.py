import logging
from typing import Any, Optional
from datetime import datetime
from django.http import JsonResponse

from osshared.response.enum import enumResponseStatus
from osshared.response.response import ResponseBase

import uuid

logger = logging.getLogger(__name__)

class ResponseBuilder:


    @staticmethod
    def buildOkDict(
        data: Optional[Any] = None,
        messageId: Optional[str] = "backend.common.ok",
        traceId: Optional[str] = None
    ) -> dict:
        logger.debug("buildOkDict")
        
        varResponse: ResponseBase = ResponseBase(
            status=enumResponseStatus.OK.value,
            messageId=messageId,
            data=data,
            traceId=traceId or str(uuid.uuid4()),
            timestamp=datetime.now().isoformat(),
        )
        
        varReturn: dict = varResponse.model_dump()
        return varReturn
    
    
    @staticmethod
    def buildErrorDict(
        messageId: Optional[str] = "backend.message.baseException",
        errors: Optional[Any] = None,
        traceId: Optional[str] = None
    ) -> dict:
        logger.debug("buildErrorDict")
        
        varResponse: ResponseBase = ResponseBase(
            status=enumResponseStatus.CUSTOM.value,
            messageId=messageId,
            errors=errors,
            traceId=traceId or str(uuid.uuid4()),
            timestamp=datetime.now().isoformat(),
        )
        
        varReturn: dict = varResponse.model_dump()
        return varReturn
    
    
    @staticmethod
    def buildExceptionDict(
        messageId: Optional[str] = "backend.message.baseException",
        errors: Optional[Any] = None,
        traceId: Optional[str] = None
    ) -> dict:
        logger.debug("buildExceptionDict")
        
        varResponse: ResponseBase = ResponseBase(
            status=enumResponseStatus.ERROR.value,
            messageId=messageId,
            errors=errors,
            traceId=traceId or str(uuid.uuid4()),
            timestamp=datetime.now().isoformat(),
        )
        
        varReturn: dict = varResponse.model_dump()
        return varReturn
