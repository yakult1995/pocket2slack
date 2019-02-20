import os
import requests
import webbrowser

POCKET_REDIRECT_URL = 'http://localhost:80'


def get_request_token():
    payload = {
        'consumer_key': os.environ['CONSUMER_KEY'],
        'redirect_uri': POCKET_REDIRECT_URL
    }
    r = requests.post('https://getpocket.com/v3/oauth/request', data=payload)

    print('request_token: ', r.text.split('=')[1])
    return r.text.split('=')[1]


def get_access_token(request_token):
    payload = {
        'consumer_key': os.environ['CONSUMER_KEY'],
        'code': request_token
    }
    r = requests.post('https://getpocket.com/v3/oauth/authorize', data=payload)
    print('access_token: ', r.text.split('=')[1].split('&')[0])


code = get_request_token()
webbrowser.open('https://getpocket.com/auth/authorize?request_token={0}&redirect_uri={1}'.format(code, POCKET_REDIRECT_URL))
input()
get_access_token(code)
