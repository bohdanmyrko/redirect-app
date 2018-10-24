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
        self.ensure_ascii = True

    def post(self, request):
        date = request.POST.get('DATE', '')
        if not date:
            return JsonResponse({'status': 422, 'message': 'DATE param is required'})
        else:
            self.ftp_con = utils.connect_ftp(request.POST["HOST"],
                                             request.POST["LOGIN"],
                                             request.POST["PASSWORD"])
            if self.ftp_con is None:
                return HttpResponse('Can`t connect to FTP', status=522)
            else:
                self.filenames = self.ftp_con.nlst()
                if self.filenames:
                    self.process_response.after_response(self, request)
                    return JsonResponse({'status': 200, 'message': 'Connect to ftp. Start preparing data.'})
                else:
                    return JsonResponse({'status': 204, 'message': 'No files was found'})

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
        try:
            for file in self.dateToFileDict.values():
                self.ftp_con.retrbinary('RETR ' + file, bd.save_data_to_buff, 1024)
                bd.save_data_to_buff(config['FILE_DELIMITER'].encode(charset))
            return bd.buffer
        finally:
            self.ftp_con.quit()
        # return bd.buffer.decode('cp1251').encode('utf-8')

    def prepare_data(self, request):
        self.create_date_file_dict(request.POST['DATE'])
        if self.dateToFileDict:
            binary_data = self.download_by_date(request.POST.get('CHARSET', config['CHARSET']))
            string_data = binary_data.decode('cp1251')
            data = {'data': string_data}
            return data
        else:
            logger.info('STATUSES: No files was found')

    @after_response.enable
    def process_response(self, request):
        logger.debug('STATUSES: After response process started')
        sf_token, json_creds = utils.process_auth_meta(request.META['HTTP_AUTHORIZATION'])
        if sf_token is not None:
            headers = {'Authorization': 'Bearer ' + sf_token, 'Content-Type': 'application/json'}
            data = self.prepare_data(request)
            utils.make_request_to_sf(json_creds, data, headers, self.ensure_ascii)
        else:
            logger.warning('STATUSES: INVALID TOKEN')


class StatusWthFilenameView(StatusesView):
    def prepare_data(self, request):
        try:
            self.create_date_file_dict(request.POST['DATE'])
            self.ensure_ascii = False
            if self.dateToFileDict:
                setattr(self, 'data', dict.fromkeys(list(self.dateToFileDict.values()), ''))
                for file in self.dateToFileDict.values():
                    self.ftp_con.retrbinary('RETR ' + file, self.update_dict(file))
                return self.data
            else:
                logger.info('STATUSES: No files was found')
        except Exception as e:
            logger.exception('Exception occurred')
        finally:
            self.ftp_con.quit()

    def update_dict(self, filename):
        def func_to_return(file_data):
            if file_data is None:
                self.data[filename] = ''
            else:
                self.data[filename] = bytes(file_data).decode('utf-8')

        return func_to_return

    def delete(self, request):
        self.ftp_con = utils.connect_ftp(request.DELETE["HOST"],
                                         request.DELETE["LOGIN"],
                                         request.DELETE["PASSWORD"])
        if self.ftp_con is None:
            return HttpResponse('Can`t connect to FTP', status=522)
        else:
            file_names = request.DELETE['FILENAMES']
            ftp_files = self.ftp_con.nlst()

            for name in file_names:
                if name in ftp_files:
                    print('DELETE')


@method_decorator(csrf_exempt, name='dispatch')
class PricesView(View):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ftp_con = None

    def post(self, request):
        self.ftp_con = utils.connect_ftp(request.POST["HOST"],
                                         request.POST["LOGIN"],
                                         request.POST["PASSWORD"])
        if self.ftp_con is None:
            return HttpResponse('Can`t connect to FTP', status=522)
        else:
            filename = request.POST['FILENAME']
            logger.info(f'PRICES: File to download: {filename}')

            if filename in self.ftp_con.nlst():
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
