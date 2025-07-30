import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger("osshared.middleware.requestLogging")

class classRequestLoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        logger.debug(f"[REQUEST] {request.method} {request.get_full_path()}")

    def process_response(self, request, response):
        logger.debug(f"[RESPONSE] {request.method} {request.get_full_path()} → {response.status_code}")
        return response
