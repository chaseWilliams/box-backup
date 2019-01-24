from boxsdk.object.file import File
from boxsdk.exception import BoxAPIException
from time import sleep
class FileDownload:
    def __init__(self, file_id, file_path):
        self.file_id = file_id
        self.file_path = file_path
    
    def perform(self, session):
        box_f = File(session, self.file_id)
        with open(self.file_path, 'wb') as f:
            while True:
                try: 
                    box_f.download_to(f)
                    break
                except BoxAPIException:
                    # most likely invalid access token, sleep and retry
                    sleep(1)


class RunningTotal:
    def __init__(self, msg):
        self.count = -1
        self.msg = msg
        self.next()

    def next(self):
        self.count += 1
        print(self.msg, self.count, end='\r')