from osshared.log.logger import methodGetLogger
from typing import Any, Optional
from datetime import datetime
from django.http import JsonResponse

from osshared.response.enum import enumResponseStatus
from osshared.response.response import classResponseBase

import uuid

logger = methodGetLogger(__name__)

class classResponseBuilder:


    @staticmethod
    def methodBuildOkDict(
        data: Optional[Any] = None,
        messageId: Optional[str] = "backend.common.ok",
        traceId: Optional[str] = None
    ) -> dict:
        logger.debug("methodBuildOkDict")
        
        varResponse: classResponseBase = classResponseBase(
            status=enumResponseStatus.OK.value,
            messageId=messageId,
            data=data,
            traceId=traceId or str(uuid.uuid4()),
            timestamp=datetime.now().isoformat(),
        )
        
        varReturn: dict = varResponse.model_dump()
        return varReturn
    
    
    @staticmethod
    def methodBuildErrorDict(
        messageId: Optional[str] = "backend.message.baseException",
        errors: Optional[Any] = None,
        traceId: Optional[str] = None
    ) -> dict:
        logger.debug("methodBuildErrorDict")
        
        varResponse: classResponseBase = classResponseBase(
            status=enumResponseStatus.CUSTOM.value,
            messageId=messageId,
            errors=errors,
            traceId=traceId or str(uuid.uuid4()),
            timestamp=datetime.now().isoformat(),
        )
        
        varReturn: dict = varResponse.model_dump()
        return varReturn
    
    
    @staticmethod
    def methodBuildExceptionDict(
        messageId: Optional[str] = "backend.message.baseException",
        errors: Optional[Any] = None,
        traceId: Optional[str] = None
    ) -> dict:
        logger.debug("methodBuildExceptionDict")
        
        varResponse: classResponseBase = classResponseBase(
            status=enumResponseStatus.ERROR.value,
            messageId=messageId,
            errors=errors,
            traceId=traceId or str(uuid.uuid4()),
            timestamp=datetime.now().isoformat(),
        )
        
        varReturn: dict = varResponse.model_dump()
        return varReturn
