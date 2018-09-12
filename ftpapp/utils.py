from ftplib import FTP


def connect_ftp(request):
    ftp = FTP()
    try:
        print('TRYING TO CONNECT')
        print(request.POST['HOST'])
        print(request.POST['LOGIN'])
        print(request.POST['PASSWORD'])
        res = ftp.connect(request.POST['HOST'])
        print(res)
        login = ftp.login(request.POST['LOGIN'], request.POST['PASSWORD'])
        print(login)
    except Exception as e:
        return
    else:
        print(f'Connection to {ftp.host} success!')
        return ftp


def check_file_curried(filename):
    def check_file(ftp_file):
        if ftp_file == filename:
            return True
        else:
            raise FileNotFoundError
    return check_file
