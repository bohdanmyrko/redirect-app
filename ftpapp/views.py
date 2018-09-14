import requests
import base64

from ftpapp import auth, utils
from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View
from ftplib import FTP
import datetime
import json
import after_response

with open('config.json', 'r') as f:
    config = json.load(f)

filenames = []
dateToFileDict = {}


class BinaryData:
    def __init__(self):
        self.buffer = b''

    def save_data_to_buff(self, data):
        self.buffer += data


def download_by_date(ftp, filenames, charset):
    bd = BinaryData()
    for file in filenames:
        retr = ftp.retrbinary('RETR ' + file, bd.save_data_to_buff, 1024)
        bd.save_data_to_buff(config['FILE_DELIMITER'].encode(charset))

    ftp.quit()
    return bd.buffer.decode('cp1251').encode('utf-8')


def download_by_name(ftp, filename):
    bd = BinaryData()
    retr = ftp.retrbinary('RETR ' + filename, bd.save_data_to_buff, 1024)
    ftp.quit()
    return bd.buffer.decode('cp1251').encode('utf-8')


def add_filename(arg):
    splited_line = arg.split(' ')
    filename = splited_line[-1]
    filenames.append(filename)


def create_date_file_dict(ftp, req_date):
    request_date = datetime.datetime.strptime(req_date, config['DATE_FORMAT'])
    for filename in filenames:
        response = ftp.sendcmd('MDTM ' + filename)
        response = response.split(' ')
        file_date = datetime.datetime.strptime(response[1], config['DATE_FORMAT'])

        if file_date > request_date:
            dateToFileDict[file_date] = filename


@csrf_exempt
def connectftp(request):
    print(filenames)
    filenames.clear()
    dateToFileDict.clear()
    if request.method == 'POST':
        date = request.POST.get('DATE', '')
        if not date:
            return JsonResponse({'status': 422, 'message': 'DATE param is required'})
        else:
            ftp = FTP()
            ftp.connect(request.POST.get('HOST', config['HOST']), int(request.POST.get('PORT', config['PORT'])))
            ftp.login(request.POST.get('LOGIN', config['LOGIN']), request.POST.get('PASSWORD', config['PASSWORD']))
            print('Connection!')
            result = ftp.retrlines('LIST', add_filename)
            if '226' in result:
                create_date_file_dict(ftp, date)

            binary_data = download_by_date(ftp, dateToFileDict.values(), request.POST.get('CHARSET', config['CHARSET']))
            return HttpResponse(binary_data, content_type='application/x-binary')


@method_decorator(csrf_exempt, name='dispatch')
class FileByNameView(View):
    pass


@method_decorator(csrf_exempt, name='dispatch')
class FileWNameView(View):

    def post(self, request, *args, **kwargs):
        ftp_con = utils.connect_ftp(request)
        if ftp_con is None:
            return HttpResponse('Can`t connect to FTP', status = 522)
        else:
            filename = request.POST['FILENAME']
            if ftp_con.retrlines('NLST', utils.check_file_curried(filename)):
                process_after_response.after_response(ftp_con, filename,request.META['HTTP_AUTHORIZATION'])
                return HttpResponse('Success', status = 200)
            else:
                return HttpResponse(f'File {filename} doesn`t exist', status = 404)


@after_response.enable
def process_after_response(ftp_con, filename,meta):
    print('After Response')
    sf_url = 'https://epd-vision--turkeyimp.cs89.my.salesforce.com/services/apexrest/medservice/price/'
    binary_data = download_by_name(ftp_con, filename)

    decoded_meta = base64.b64decode(meta)
    json_creds = json.loads(decoded_meta)
    token = auth.get_token_to_sf(**json_creds)

    if token is not None:
        string_data = binary_data.decode('utf-8').replace('\r\n', '')
        headers = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}
        data = {'data': string_data, 'city_code': filename.split('.')[0]}
        response = requests.post(url=sf_url, data=json.dumps(data), headers=headers)
        print(f'Response status : {response.status_code}')
    else:
        print('Invalid token')
