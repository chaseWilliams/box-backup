from boxsdk import OAuth2, Client
from tqdm import trange
import numpy as np
import datetime
from threading import Thread, current_thread
import os
import json

FOLDER_ID = int(input('Folder ID (or 0 for root)\n>'))
ROOT_PATH = os.path.join(local_path, 'backup-' + str(datetime.datetime.now()))
os.mkdir(backup_path)
THREADS = 10

class FileDownload:
    def __init__(self, file_ref, file_path):
        self.file_ref = file_ref
        self.file_path = file_path
    
    def perform(self):
        with open(self.file_path, 'wb') as f:
            self.file_ref.download_to(f)

class RunningTotal:
    def __init__(self, msg):
        self.count = -1
        self.msg = msg
        self.next()

    def next(self):
        self.count += 1
        print(self.msg, self.count, end='\r')


with open('private.json', 'r') as f:
    auth = json.loads(f.read())

client = Client(OAuth2(
    client_id=auth['boxAppSettings']['clientID'],
    client_secret=auth['boxAppSettings']['clientSecret'],
    access_token='dsLpeFNnlXHiZfc5dFgUIRjsGT7jU8DS'
))
file_downloads = []
print("Mapping Box directories")
rt = RunningTotal("Directories indexed:")

def get_folder_items(folder_id, file_path):
    rt.next()
    items = client.folder(folder_id=folder_id).get_items()
    for item in items:
        item_path = os.path.join(file_path, item.name)
        if item.type == 'file':
            file_downloads.append(FileDownload(
                item,
                item_path
            ))
        elif item.type == 'folder':
            try: # create the folder if nonexistent on host
                os.mkdir(item_path)
            except:
                pass
            get_folder_items(
                item.id,
                item_path
            )

def worker_task(file_downloads, position):
    text = "Thread #{0}".format(position)
    for i in trange(len(file_downloads), desc=text, position=position):
        file_downloads[i].perform()

get_folder_items(FOLDER_ID, ROOT_PATH)

# set up the workers
chunked_file_downloads = np.array_split(file_downloads, THREADS)

workers = []
for i, _chunked_file_download in enumerate(chunked_file_downloads):
    workers.append(Thread(target=worker_task, args=(_chunked_file_download, i)))

for worker in workers:
    worker.start()

for worker in workers:
    worker.join()

print("\n" * (THREADS - 1)) # move to next line after tqdm's progress bars
print(len(file_downloads), 'files downloaded')
