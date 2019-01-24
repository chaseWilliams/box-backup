from boxsdk import Client
from boxsdk.auth import RedisManagedOAuth2
from boxsdk.session.session import AuthorizedSession
from lib.helpers import RunningTotal, FileDownload
from lib.auth import get_authenticated_client
from tqdm import trange
import numpy as np
import datetime
from threading import Thread, current_thread
import os
import json

FOLDER_ID = int(input('Folder ID (or 0 for root)\n>'))
ROOT_PATH = os.path.join(os.getcwd(), 'backup-' + str(datetime.datetime.now()))
os.mkdir(ROOT_PATH)
THREADS = 10

client = get_authenticated_client()

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
                item.id,
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
    with open('private.json', 'r') as f:
        auth = json.loads(f.read())

    oauth = RedisManagedOAuth2(
        client_id=auth['boxAppSettings']['clientID'],
        client_secret=auth['boxAppSettings']['clientSecret'],
        unique_id='foo',
    )
    session = AuthorizedSession(oauth)
    for i in trange(len(file_downloads), desc=text, position=position):
        file_downloads[i].perform(session)

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
