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
        hostname, directory = parse_host(request.POST['HOST'])
        ftp.connect(hostname)
        ftp.login(request.POST['LOGIN'], request.POST['PASSWORD'])
        if directory is not None:
            logger.info(f'Changing directory to: {directory}')
            ftp.cwd(directory)

    except Exception as e:
        logger.exception(f"Exception occurred during connecting to {ftp.host}")
        return
    else:
        logger.info(f'CONNECTED TO {ftp.host}')
        return ftp


def parse_host(host_param):
    splitted_host = host_param.split('/')
    if len(splitted_host) == 1:
        return splitted_host[0], None
    else:
        hostname, directory, *_ = splitted_host
        return hostname, directory


def make_request_to_sf(json_creds, data, headers):
    try:
        logger.debug('Try to make request to sf')
        logger.debug(json_creds["sf_url"])
        logger.debug(data)
        logger.debug(json.dumps(data, ensure_ascii=False).encode('utf-8'))
        response = requests.post(url=json_creds["sf_url"], data=json.dumps(data, ensure_ascii=False).encode('utf-8'), headers=headers)
    except Exception as e:
        logging.exception("Exception occurred")
    else:
        logger.info(f'Response status from sf: {response.status_code}')


def process_auth_meta(auth_header):
    decoded_creds = base64.b64decode(auth_header)
    json_creds = json.loads(decoded_creds)
    sf_token = auth.get_token_to_sf(**json_creds)
    return sf_token, json_creds
