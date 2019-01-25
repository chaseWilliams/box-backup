from boxsdk import Client
from boxsdk.auth import RedisManagedOAuth2
from boxsdk.session.session import AuthorizedSession
from lib.helpers import RunningTotal, FileDownload
from lib.auth import get_oauth
from tqdm import trange
import numpy as np
import datetime
from threading import Thread, current_thread
import os
import json

FOLDER_ID = int(input('Folder ID (or 0 for root)\n>'))
ROOT_PATH = os.path.join(os.getcwd(), 'backup-' + str(datetime.datetime.now()))
os.mkdir(ROOT_PATH)
THREADS = 7

oauth = get_oauth()
client = Client(oauth)

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

def worker_task(file_downloads, position, oauth):
    text = "Thread #{0}".format(position)
    for i in trange(len(file_downloads), desc=text, position=position):
        file_downloads[i].perform(oauth)

get_folder_items(FOLDER_ID, ROOT_PATH)
print()
# set up the workers
chunked_file_downloads = np.array_split(file_downloads, THREADS)

workers = []
for i, _chunked_file_download in enumerate(chunked_file_downloads):
    workers.append(Thread(target=worker_task, args=(_chunked_file_download, i, oauth)))

for worker in workers:
    worker.start()

for worker in workers:
    worker.join()

print("\n" * (THREADS - 1)) # move to next line after tqdm's progress bars
print(len(file_downloads), 'files downloaded')
