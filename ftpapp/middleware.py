import json
import logging

logger = logging.getLogger(__name__)


class HttpDeleteMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method.lower() == 'delete':
            logger.info('Entering HTTP DELETE middleware')
            request_body = request.body.decode('utf-8')
            body = json.loads(request_body)
            request.DELETE = body

        response = self.get_response(request)
        return response
