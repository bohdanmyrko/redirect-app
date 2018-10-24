import json


class HttpDeleteMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print(request)
        if request.method.lower() == 'delete':
            request_body = request.body.decode('utf-8')
            body = json.loads(request_body)
            request.DELETE = body
            print(request.DELETE)
        response = self.get_response(request)
        return response
