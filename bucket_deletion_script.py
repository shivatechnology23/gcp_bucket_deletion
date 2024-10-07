from google.cloud import storage
from collections import defaultdict
from datetime import datetime, timezone

def get_folder_creation_dates(bucket_name):
    """
    Function to get the earliest creation date of each folder and subfolder in the bucket.
    """
    
    storage_client = storage.Client()

    
    folder_creation_dates = defaultdict(lambda: None)

    
    blobs = storage_client.list_blobs(bucket_name)

    for blob in blobs:
        # Split the object name by '/' to extract folder/subfolder paths
        folder_parts = blob.name.split('/')[:-1]  
        folder_path = "/".join(folder_parts)  

        # Get the object's creation time
        creation_time = blob.time_created

        # If this folder doesn't have a recorded creation date or has a later date, update it
        if folder_creation_dates[folder_path] is None or creation_time < folder_creation_dates[folder_path]:
            folder_creation_dates[folder_path] = creation_time

    return folder_creation_dates

def delete_folders_with_keywords(bucket_name, keywords, days_old):
    """
    Function to delete folders that contain the specified keywords and are older than a certain number of days.
    Also logs the deletion activity along with creation times.
    """
    
    storage_client = storage.Client()

    # Get the current timezone-aware date
    current_date = datetime.now(timezone.utc)  # Make datetime.now() timezone-aware

    # Get the creation dates of all folders and subfolders in the bucket
    folder_creation_dates = get_folder_creation_dates(bucket_name)

    # Open the log file to record deleted file names and creation times
    with open("deleted_files.log", "a") as log_file:
        
        blobs = storage_client.list_blobs(bucket_name)
        
        for blob in blobs:
            
            folder_parts = blob.name.split('/')[:-1]
            folder_path = "/".join(folder_parts)
            
            # Get the folder's creation date
            folder_creation_date = folder_creation_dates.get(folder_path, None)
            
            # If the folder's creation date exists and is older than the specified number of days
            if folder_creation_date and (current_date - folder_creation_date).days > days_old:
                # Check if the folder path contains any of the keywords
                if any(keyword in folder_path for keyword in keywords):
                    # Log the blob's name and creation time
                    log_message = f"Deleted: {blob.name}, Created: {blob.time_created.isoformat()}"
                    
                    # Delete the blob (object)
                    blob.delete()
                    
                    # Print the log information on screen
                    print(log_message)

                    # Log the deleted file name and creation time to the log file
                    log_file.write(log_message + "\n")
    
    print(f"All folders containing {', '.join(keywords)} and older than {days_old} days deleted.")

# Usage
bucket_name = "dipak001"
keywords = ["dev", "uat"]  # Keywords to look for in folder names
days_old = 1  # Number of days threshold for deletion

delete_folders_with_keywords(bucket_name, keywords, days_old)
