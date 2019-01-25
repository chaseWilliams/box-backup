from boxsdk.object.file import File
from boxsdk.exception import BoxAPIException
from boxsdk.session.session import AuthorizedSession
import redis as rd
from time import sleep

class FileDownload:
    def __init__(self, file_id, file_path):
        self.file_id = file_id
        self.file_path = file_path
        self.db = rd.Redis()
    
    def perform(self, oauth):
        session = AuthorizedSession(oauth)
        box_f = File(session, self.file_id)
        with open(self.file_path, 'wb') as f:
            while True:
                try:
                    box_f.download_to(f)
                    break
                except BoxAPIException:
                    if not self.db.get('refreshing').decode('utf-8') == 'true':
                        self.db.set('refreshing', 'true')
                        oauth.refresh(oauth.access_token)
                        self.db.set('refreshing', 'false')
                    else:
                        sleep(3)

class RunningTotal:
    def __init__(self, msg):
        self.count = -1
        self.msg = msg
        self.next()

    def next(self):
        self.count += 1
        print(self.msg, self.count, end='\r')