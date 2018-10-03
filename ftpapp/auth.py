from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import LegacyApplicationClient


#token_url = 'https://test.salesforce.com/services/oauth2/token'


def get_token_to_sf(**kwargs):
    try:
        oauth = OAuth2Session(client=LegacyApplicationClient(kwargs['client_id']))
        if oauth.client_id is not None:
            token = fetch_sf_token(oauth, **kwargs)
            if token is not None:
                return token
            else:
                return fetch_sf_token(oauth, **kwargs)

        else:
            print('There is no client_id')
    except Exception as e:
        print('Error:', e)


def fetch_sf_token(oauth, **kwargs):
    print(kwargs)
    token = oauth.fetch_token(token_url=kwargs['token_url'], username=kwargs['username'], password=kwargs['password'],
                              client_id=kwargs['client_id'],
                              client_secret=kwargs['client_secret'])
    return token['access_token']
