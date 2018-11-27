import after_response
import requests
import logging
import google-api-python-client
from django.http import HttpResponseRedirect, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from ftpapp import utils

logger = logging.getLogger(__name__)


#
# @csrf_exempt
# def prices(request):
#     if request.method == 'POST':
#         print(request.POST['url'])
#         response = requests.get(
#             request.POST['url'], verify=False,
#             stream=True)
#         return HttpResponse(response.raw.read().decode('cp1251').encode('utf-8'))
#         # return HttpResponse(json.dumps({space : response}))

@csrf_exempt
def clients(request):
    if request.method == 'POST':
        print(request.POST['url'])
        response = requests.get(
            request.POST['url'], verify=False,
            stream=True)
        return HttpResponse(response.raw.read())


@csrf_exempt
def bills(request):
    if request.method == 'POST':
        logger.debug('Bills request')
        logger.debug(f'BILLS: request: {request.POST}')
        url = request.POST['url']
        body = request.POST['body']
        if url and body:
            process_after_response.after_response(url, body, request.POST['orderid'],
                                                  request.META['HTTP_AUTHORIZATION'])
            return HttpResponse('Success', 200)
        else:
            logger.warning('BILLS: invalid post params')
            return HttpResponse('Invalid post params', 400)


@csrf_exempt
def images(request):
    file_metadata = {'name': 'photo.jpg'}
    media = MediaFileUpload('files/photo.jpg',
                        mimetype='image/jpeg')
    file = drive_service.files().create(body=file_metadata,
                                    media_body=media,
                                    fields='id').execute()
    # print 'File ID: %s' % file.get('id')  

@after_response.enable
def process_after_response(url, body, orderid, auth_header, ):
    logger.debug('BILLS: After response process started')
    sf_token, json_creds = utils.process_auth_meta(auth_header)
    if sf_token is not None:
        try:
            response = requests.post(url, data={'BODY': body}, verify=False, stream=True)
            logger.debug(f'BILLS: response: {response.text}')
        except Exception as e:
            logger.exception('Exception occurred')
        else:
            headers = {'Authorization': 'Bearer ' + sf_token, 'Content-Type': 'application/json'}
            data = {'externalId': orderid, 'data': response.text, 'content': response.headers['Content-Type']}
            utils.make_request_to_sf(json_creds, data, headers)
    else:
        logger.warning('PRICES: INVALID TOKEN')
