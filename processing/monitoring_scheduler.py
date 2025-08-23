# processing/monitoring_scheduler.py

import schedule
import time
import json
import os
from datetime import datetime, timedelta
import subprocess
import sys

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MONITORING_TASKS_FILE = os.path.join(BASE_DIR, 'monitoring_tasks.json')
GEE_DOWNLOAD_SCRIPT = os.path.join(BASE_DIR, 'gee_drive_download.py')
GEE_CHANGE_DETECTION_SCRIPT = os.path.join(BASE_DIR, 'gee_change_detection.py')
UNET_INFERENCE_SCRIPT = os.path.join(BASE_DIR, 'unet_inference.py')
PYTHON_PATH = sys.executable

def get_monitoring_tasks():
    """Reads monitoring tasks from the state file."""
    if not os.path.exists(MONITORING_TASKS_FILE):
        return []
    with open(MONITORING_TASKS_FILE, 'r') as f:
        return json.load(f)

def save_monitoring_tasks(tasks):
    """Saves monitoring tasks to the state file."""
    with open(MONITORING_TASKS_FILE, 'w') as f:
        json.dump(tasks, f, indent=4)

def run_python_script(script_path, args):
    """Helper to run a Python script and return its JSON output."""
    try:
        command = [PYTHON_PATH, script_path] + args
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        # Assuming the last line is the JSON output
        last_line = result.stdout.strip().split('\n')[-1]
        return json.loads(last_line)
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_path}: {e.stderr}", file=sys.stderr)
        # We need to catch this specific error and handle it gracefully
        # The stderr from the subprocess will contain the JSON error message from gee_drive_download.py
        if 'Processing Error: Failed to download' in e.stderr:
            raise Exception("Processing Error: Failed to download images due to cloud occlusion or other issues.")
        raise
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {script_path}: {e}", file=sys.stderr)
        raise

def monitor_aois():
    """
    The core function that the scheduler will run.
    It checks all AOIs and triggers processing if a new image is due.
    """
    print(f"[{datetime.now().isoformat()}] Checking for AOIs to monitor...")
    monitoring_tasks = get_monitoring_tasks()
    
    updated_tasks = []
    
    if not monitoring_tasks:
        print("No monitoring tasks found. Waiting for new tasks to be added.")
        return # Exit the function early

    for task in monitoring_tasks:
        aoi_id = task['aoi_id']
        last_checked_date_str = task.get('last_checked_date')
        monitoring_interval = task['monitoring_interval_days']
        threshold = task['threshold']
        geojson_str = json.dumps(task['geojson'])
        
        # Determine the date for the new image and the baseline image
        current_date = datetime.now()
        
        # We need a longer date range for the new image to find a cloud-free image
        # This is a crucial change to handle the download failure
        # Let's search for an image in the last 7 days from today.
        end_date = current_date.strftime('%Y-%m-%d')
        start_date = (current_date - timedelta(days=7)).strftime('%Y-%m-%d')

        # Use the last checked date for the baseline image
        # If there's no last_checked_date, use a longer period, e.g., 30 days before the new image
        if not last_checked_date_str:
            baseline_start_date = (current_date - timedelta(days=37)).strftime('%Y-%m-%d')
            baseline_end_date = (current_date - timedelta(days=30)).strftime('%Y-%m-%d')
        else:
            baseline_start_date = last_checked_date_str
            baseline_end_date = last_checked_date_str

        if not last_checked_date_str or (current_date > datetime.strptime(last_checked_date_str, '%Y-%m-%d') + timedelta(days=monitoring_interval)):
            print(f"AOI {aoi_id}: New image is due. Searching for a cloud-free image...")
            
            try:
                # 1. Download images for two dates with a flexible search range
                download_result = run_python_script(GEE_DOWNLOAD_SCRIPT, [geojson_str, baseline_start_date, end_date])

                if download_result.get('status') != 'success':
                    # This check is now redundant since the error is caught by the try/except block.
                    # It's good practice to leave it, but the raised exception will handle the failure.
                    raise Exception(f"Download failed: {download_result.get('message')}")
                
                t1_path = download_result['t1_path']
                t2_path = download_result['t2_path']
                
                # 2. Run change detection scripts in parallel
                ndvi_result = run_python_script(GEE_CHANGE_DETECTION_SCRIPT, [t1_path, t2_path, str(threshold)])
                unet_result = run_python_script(UNET_INFERENCE_SCRIPT, [t1_path, t2_path])
                
                # 3. Combine results and check against threshold
                ndvi_change = ndvi_result['summary']['percentage_change']
                unet_change = unet_result['percentage_change']
                combined_change = (ndvi_change + unet_change) / 2

                if combined_change > (threshold * 100):
                    print(f"ALERT! Significant change detected for AOI {aoi_id}: {combined_change:.2f}% (Threshold: {threshold*100:.2f}%)")
                else:
                    print(f"AOI {aoi_id}: No significant change detected. Combined change: {combined_change:.2f}%")

                # 4. Update the last checked date
                task['last_checked_date'] = end_date
                updated_tasks.append(task)
            
            except Exception as e:
                # This is the new, more robust error handling
                # We specifically check for the download failure and skip this task for now
                if "Failed to download images" in str(e):
                    print(f"AOI {aoi_id}: Skipping monitoring for now. Could not find a cloud-free image in the recent date range.", file=sys.stderr)
                    # Do not update the last_checked_date so it's retried on the next run
                    updated_tasks.append(task)
                else:
                    # For all other errors, we still report them and add the task back to the list
                    print(f"AOI {aoi_id}: Failed to process. Error: {e}", file=sys.stderr)
                    updated_tasks.append(task)
        
        else:
            updated_tasks.append(task)

    save_monitoring_tasks(updated_tasks)
    print(f"Finished checking monitoring tasks. Next check in {monitoring_interval} days.")

if __name__ == "__main__":
    print("Starting monitoring scheduler...")
    schedule.every(5).minutes.do(monitor_aois)
    
    while True:
        schedule.run_pending()
        time.sleep(1)








































































# import schedule
# import time
# import json
# import os
# from datetime import datetime, timedelta
# import subprocess
# import sys

# # Define paths
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# MONITORING_TASKS_FILE = os.path.join(BASE_DIR, 'monitoring_tasks.json')
# GEE_DOWNLOAD_SCRIPT = os.path.join(BASE_DIR, 'gee_drive_download.py')
# GEE_CHANGE_DETECTION_SCRIPT = os.path.join(BASE_DIR, 'gee_change_detection.py')
# UNET_INFERENCE_SCRIPT = os.path.join(BASE_DIR, 'unet_inference.py')
# PYTHON_PATH = sys.executable

# def get_monitoring_tasks():
#     """Reads monitoring tasks from the state file."""
#     if not os.path.exists(MONITORING_TASKS_FILE):
#         return []
#     with open(MONITORING_TASKS_FILE, 'r') as f:
#         return json.load(f)

# def save_monitoring_tasks(tasks):
#     """Saves monitoring tasks to the state file."""
#     with open(MONITORING_TASKS_FILE, 'w') as f:
#         json.dump(tasks, f, indent=4)

# def run_python_script(script_path, args):
#     """Helper to run a Python script and return its JSON output."""
#     try:
#         command = [PYTHON_PATH, script_path] + args
#         result = subprocess.run(command, capture_output=True, text=True, check=True)
#         # Assuming the last line is the JSON output
#         last_line = result.stdout.strip().split('\n')[-1]
#         return json.loads(last_line)
#     except subprocess.CalledProcessError as e:
#         print(f"Error running {script_path}: {e.stderr}", file=sys.stderr)
#         raise
#     except json.JSONDecodeError as e:
#         print(f"Error decoding JSON from {script_path}: {e}", file=sys.stderr)
#         raise

# def monitor_aois():
#     """
#     The core function that the scheduler will run.
#     It checks all AOIs and triggers processing if a new image is due.
#     """
#     print(f"[{datetime.now().isoformat()}] Checking for AOIs to monitor...")
#     monitoring_tasks = get_monitoring_tasks()
    
#     updated_tasks = []
    
#     if not monitoring_tasks:
#         print("No monitoring tasks found. Waiting for new tasks to be added.")
#         return # Exit the function early

#     for task in monitoring_tasks:
#         aoi_id = task['aoi_id']
#         last_checked_date_str = task.get('last_checked_date')
#         monitoring_interval = task['monitoring_interval_days']
#         threshold = task['threshold']
#         geojson_str = json.dumps(task['geojson'])
        
#         # Determine the date for the new image and the baseline image
#         current_date = datetime.now()
#         start_date_str = last_checked_date_str if last_checked_date_str else (current_date - timedelta(days=monitoring_interval)).strftime('%Y-%m-%d')
#         end_date_str = current_date.strftime('%Y-%m-%d')

#         if not last_checked_date_str or (current_date > datetime.strptime(last_checked_date_str, '%Y-%m-%d') + timedelta(days=monitoring_interval)):
#             print(f"AOI {aoi_id}: New image is due. Fetching image...")
            
#             try:
#                 # 1. Download images for two dates
#                 download_result = run_python_script(GEE_DOWNLOAD_SCRIPT, [geojson_str, start_date_str, end_date_str])

#                 if download_result.get('status') != 'success':
#                     raise Exception(f"Download failed: {download_result.get('message')}")
                
#                 t1_path = download_result['t1_path']
#                 t2_path = download_result['t2_path']
                
#                 # 2. Run change detection scripts in parallel
#                 ndvi_result = run_python_script(GEE_CHANGE_DETECTION_SCRIPT, [t1_path, t2_path, str(threshold)])
#                 unet_result = run_python_script(UNET_INFERENCE_SCRIPT, [t1_path, t2_path])
                
#                 # 3. Combine results and check against threshold
#                 ndvi_change = ndvi_result['summary']['percentage_change']
#                 unet_change = unet_result['percentage_change']
#                 combined_change = (ndvi_change + unet_change) / 2

#                 if combined_change > (threshold * 100):
#                     print(f"ALERT! Significant change detected for AOI {aoi_id}: {combined_change:.2f}% (Threshold: {threshold*100:.2f}%)")
#                     # You would integrate an email sending logic here, similar to your Node.js controller.
#                     # Or, you could write a file that your Node.js backend reads to trigger an email.
#                 else:
#                     print(f"AOI {aoi_id}: No significant change detected. Combined change: {combined_change:.2f}%")

#                 # 4. Update the last checked date
#                 task['last_checked_date'] = end_date_str
#                 updated_tasks.append(task)
            
#             except Exception as e:
#                 print(f"AOI {aoi_id}: Failed to process. Error: {e}", file=sys.stderr)
        
#         else:
#             updated_tasks.append(task)

#     save_monitoring_tasks(updated_tasks)
#     print(f"Finished checking monitoring tasks. Next check in {monitoring_interval} days.")

# if __name__ == "__main__":
#     print("Starting monitoring scheduler...")
#     # Schedule the monitoring function to run every 5 days for the demo.
#     # We'll use a shorter interval for demonstration purposes.
#     schedule.every(5).minutes.do(monitor_aois)
    
#     while True:
#         schedule.run_pending()
#         time.sleep(1)