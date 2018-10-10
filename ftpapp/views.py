import datetime
import json
import after_response
import logging
from ftpapp import auth, utils
from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View


logger = logging.getLogger(__name__)

with open('config.json', 'r') as f:
    config = json.load(f)


class BinaryData:
    def __init__(self):
        self.buffer = b''

    def save_data_to_buff(self, data):
        self.buffer += data


@method_decorator(csrf_exempt, name='dispatch')
class StatusesView(View):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.filenames = []
        self.dateToFileDict = {}
        self.ftp_con = None

    def post(self, request):
        date = request.POST.get('DATE', '')
        if not date:
            return JsonResponse({'status': 422, 'message': 'DATE param is required'})
        else:
            self.ftp_con = utils.connect_ftp(request)
            if self.ftp_con is None:
                return HttpResponse('Can`t connect to FTP', status=522)
            else:
                result = self.ftp_con.retrlines('LIST', self.add_filename)
                if '226' in result:
                    logger.debug(f'STATUSES: Response from ftp: {result}')
                    self.process_response.after_response(self, request)
                    return JsonResponse({'status': 200, 'message': 'Connect to ftp. Start preparing data.'})

    def add_filename(self, name_line):
        splitted_line = name_line.split(' ')
        filename = splitted_line[-1]
        self.filenames.append(filename)

    def create_date_file_dict(self, req_date):
        request_date = datetime.datetime.strptime(req_date, config['DATE_FORMAT'])
        for filename in self.filenames:
            response = self.ftp_con.sendcmd('MDTM ' + filename)
            response = response.split(' ')
            file_date = datetime.datetime.strptime(response[1], config['DATE_FORMAT'])

            if file_date > request_date:
                self.dateToFileDict[file_date] = filename

    def download_by_date(self, charset):
        bd = BinaryData()
        for file in self.filenames:
            self.ftp_con.retrbinary('RETR ' + file, bd.save_data_to_buff, 1024)
            bd.save_data_to_buff(config['FILE_DELIMITER'].encode(charset))

        self.ftp_con.quit()
        # return bd.buffer.decode('cp1251').encode('utf-8')
        return bd.buffer

    @after_response.enable
    def process_response(self, request):
        logger.debug('STATUSES: After response process started')
        sf_token, json_creds = utils.process_auth_meta(request.META['HTTP_AUTHORIZATION'])
        if sf_token is not None:
            binary_data = self.download_by_date(request.POST.get('CHARSET', config['CHARSET']))
            string_data = binary_data.decode('cp1251')
            headers = {'Authorization': 'Bearer ' + sf_token, 'Content-Type': 'application/json'}
            data = {'data': string_data}
            utils.make_request_to_sf(json_creds, data, headers)
        else:
            logger.warning('STATUSES: INVALID TOKEN')


@method_decorator(csrf_exempt, name='dispatch')
class PricesView(View):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ftp_con = None

    def post(self, request):
        self.ftp_con = utils.connect_ftp(request)
        if self.ftp_con is None:
            return HttpResponse('Can`t connect to FTP', status=522)
        else:
            filename = request.POST['FILENAME']
            logger.info(f'PRICES: File to download: {filename}')

            if self.ftp_con.retrlines('NLST', utils.check_file_curried(filename)):
                self.process_after_response.after_response(self, filename, request.META['HTTP_AUTHORIZATION'])
                return HttpResponse('Success', status=200)
            else:
                return HttpResponse(f'File {filename} doesn`t exist', status=404)

    def download_by_name(self, filename):
        bd = BinaryData()
        self.ftp_con.retrbinary('RETR ' + filename, bd.save_data_to_buff, 1024)
        self.ftp_con.quit()
        return bd.buffer.decode('cp1251').encode('utf-8')

    @after_response.enable
    def process_after_response(self, filename, auth_header):
        logger.debug('PRICES: After response process started')
        sf_token, json_creds = utils.process_auth_meta(auth_header)
        if sf_token is not None:
            binary_data = self.download_by_name(filename)
            string_data = binary_data.decode('utf-8').replace('\r\n', '')
            headers = {'Authorization': 'Bearer ' + sf_token, 'Content-Type': 'application/json'}
            data = {'data': string_data, 'city_code': filename.split('.')[0]}
            utils.make_request_to_sf(json_creds, data, headers)
        else:
            logger.warning('PRICES: INVALID TOKEN')
