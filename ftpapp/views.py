import binascii
from django.http import HttpResponseRedirect, HttpResponse
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


def downloadFile(ftp, filenames):
    bd = BinaryData()
    for file in filenames:
        retr = ftp.retrbinary('RETR ' + file, bd.save_data_to_buff, 1024)
        bd.save_data_to_buff(config['FILE_DELIMITER'].encode(config['CHARSET']))

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
    print(filenames)
    if request.method == 'POST':
        ftp = FTP('')
        ftp.connect(request.POST['HOST'])
        ftp.login(request.POST['LOGIN'], request.POST['PASSWORD'])
        print('Connection!')

        result = ftp.retrlines('LIST', addFilename)

        date = request.POST['DATE']
        if '226' in result:
            createDateFileDict(ftp, date)

        binary_data = downloadFile(ftp, dateToFileDict.values())
        print(binary_data.hex())
        return HttpResponse(binary_data, content_type='application/x-binary')
