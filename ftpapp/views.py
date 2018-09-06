import binascii
from django.http import HttpResponseRedirect, HttpResponse,JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ftplib import FTP
import datetime
import json

with open('config.json', 'r') as f:
    config = json.load(f)

filenames = []
dateToFileDict = {}


class BinaryData:
    def __init__(self):
        self.buffer = b''

    def save_data_to_buff(self, data):
        self.buffer += data


def downloadFile(ftp, filenames,charset):
    bd = BinaryData()
    for file in filenames:
        retr = ftp.retrbinary('RETR ' + file, bd.save_data_to_buff, 1024)
        bd.save_data_to_buff(config['FILE_DELIMITER'].encode(charset))

    ftp.quit()
    return bd.buffer.decode('cp1251').encode('utf-8')

def download_by_name(ftp,filename,charset):
    bd = BinaryData()
    retr = ftp.retrbinary('RETR ' + filename, bd.save_data_to_buff, 1024)
    bd.save_data_to_buff(config['FILE_DELIMITER'].encode(charset))

    ftp.quit()
    return bd.buffer.decode('cp1251').encode('utf-8')


def addFilename(arg):
    splited_line = arg.split(' ')
    filename = splited_line[-1]
    filenames.append(filename)


def createDateFileDict(ftp, req_date):
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
        date = request.POST.get('DATE','')
        if not date:
            return JsonResponse({'status': 422 ,'message': 'DATE param is required'})
        else:
            ftp = FTP()
            ftp.connect(request.POST.get('HOST', config['HOST']), int(request.POST.get('PORT', config['PORT'])))
            ftp.login(request.POST.get('LOGIN', config['LOGIN']), request.POST.get('PASSWORD', config['PASSWORD']))
            print('Connection!')
            result = ftp.retrlines('LIST', addFilename)
            if '226' in result:
                createDateFileDict(ftp, date)

            binary_data = downloadFile(ftp, dateToFileDict.values(), request.POST.get('CHARSET',config['CHARSET']))
            return HttpResponse(binary_data, content_type='application/x-binary')

@csrf_exempt
def filebyname(request):

    if request.method == 'POST':
        filename = request.POST.get('FILENAME','')
        ftp = FTP()
        ftp.connect(request.POST.get('HOST', config['HOST']))
        ftp.login(request.POST.get('LOGIN', config['LOGIN']), request.POST.get('PASSWORD', config['PASSWORD']))
        print('Connection!')
        binary_data = download_by_name(ftp, filename,request.POST.get('CHARSET',config['CHARSET']))
        print('Data has downloaded')
        return HttpResponse('200', content_type='application/x-binary')