from boxsdk import Client
from boxsdk.auth import RedisManagedOAuth2
import json

def get_authenticated_client():
    with open('private.json', 'r') as f:
        auth = json.loads(f.read())

    oauth = RedisManagedOAuth2(
        client_id=auth['boxAppSettings']['clientID'],
        client_secret=auth['boxAppSettings']['clientSecret'],
        unique_id='foo'
    )

    auth_url, csrf = oauth.get_authorization_url('http://localhost')
    print("URL:\n", auth_url)
    code = input('Code\n>')
    oauth.authenticate(code)
    return Client(oauth)