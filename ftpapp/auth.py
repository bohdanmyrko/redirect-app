from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import LegacyApplicationClient

credentials = {
    'client_id': '3MVG9sSN_PMn8tjQ7FnE6b.aE2DdeVzKTrV1ym1SqyfAqHsOFekVocn41kidwLIk12jHuAKf.6GNE8uF7FsF0',
    'client_secret': '4638048792256806838',
    'username': 'oleksandr.nedashkivskyi@abbott-cis.com.turkeyimp',
    'password': '166QLJ5Dw5u%zono%',
    'token_url': 'https://test.salesforce.com/services/oauth2/token'
}


def get_token_to_sf(client_id, token_url, client_secret, username, password):
    try:
        oauth = OAuth2Session(client=LegacyApplicationClient(client_id))
        if oauth.client_id is not None:
            token = oauth.fetch_token(token_url=token_url, username=username, password=password, client_id=client_id,
                                      client_secret=client_secret)
            return token['access_token']

        else:
            print('There is no or invalid client_id')
    except Exception as e:
        print(e)

