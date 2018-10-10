import requests
import json
import base64
import logging
from ftpapp import auth
from ftplib import FTP

logger = logging.getLogger(__name__)


def connect_ftp(request):
    ftp = FTP()
    try:
        logger.info(f'TRYING CONNECT TO {request.POST["HOST"]}')

        ftp.connect(request.POST['HOST'])
        ftp.login(request.POST['LOGIN'], request.POST['PASSWORD'])
    except Exception as e:
        logger.exception(f"Exception occurred during connecting to {ftp.host}")
        return
    else:
        logger.info(f'CONNECTED TO {ftp.host}')
        return ftp


def check_file_curried(filename):
    def check_file(ftp_file):
        if ftp_file == filename:
            return True
        else:
            return False

    return check_file


def make_request_to_sf(json_creds, data, headers):
    try:
        logger.debug('Try to make request to sf')
        response = requests.post(url=json_creds["sf_url"], data=json.dumps(data), headers=headers)
    except Exception as e:
        logging.exception("Exception occurred")
    else:
        logger.info(f'Response status from sf: {response.status_code}')


def process_auth_meta(auth_header):
    decoded_creds = base64.b64decode(auth_header)
    json_creds = json.loads(decoded_creds)
    sf_token = auth.get_token_to_sf(**json_creds)
    return sf_token, json_creds
