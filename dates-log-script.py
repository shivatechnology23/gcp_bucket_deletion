from google.cloud import storage
from collections import defaultdict
from datetime import datetime

def get_folder_creation_dates(bucket_name):

    storage_client = storage.Client()
    folder_creation_dates = defaultdict(lambda: None)
    blobs = storage_client.list_blobs(bucket_name)

    for blob in blobs:
        folder_parts = blob.name.split('/')[:-1]
        folder_path = ""

        for part in folder_parts:
            folder_path = f"{folder_path}{part}/"
            creation_time = blob.time_created

            if folder_creation_dates[folder_path] is None or creation_time < folder_creation_dates[folder_path]:
                folder_creation_dates[folder_path] = creation_time

    return folder_creation_dates


bucket_name = 'dipak001'

folder_dates = get_folder_creation_dates(bucket_name)

log_file_path = 'folder_creation_dates.log'
with open(log_file_path, 'w') as log_file:
    
    for folder, creation_date in folder_dates.items():
        log_file.write(f"Folder '{folder}' was created on: {creation_date}\n")

print(f"Folder creation dates have been logged to: {log_file_path}")
