from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import LegacyApplicationClient


def get_token_to_sf(client_id, client_secret, username, password):
    token_url = 'https://test.salesforce.com/services/oauth2/token'
    try:
        oauth = OAuth2Session(client=LegacyApplicationClient(client_id))
        if oauth.client_id is not None:
            token = oauth.fetch_token(token_url=token_url, username=username, password=password, client_id=client_id,
                                      client_secret=client_secret)
            return token['access_token']

        else:
            print('There is no client_id')
    except Exception as e:
        print('Error:', e)
