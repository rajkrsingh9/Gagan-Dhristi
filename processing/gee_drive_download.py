import ee
import json
import os
import sys
from datetime import datetime, timedelta
import time
import io
import tempfile
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import zipfile

# Define paths to credentials and token files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_FILE = os.path.join(BASE_DIR, 'credentials.json')
TOKEN_FILE = os.path.join(BASE_DIR, 'token.json')
SCOPES = ['https://www.googleapis.com/auth/drive']

def authenticate_gdrive():
    """Handles GDrive authentication for the backend."""
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=8080)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
            
    try:
        service = build('drive', 'v3', credentials=creds)
        return service
    except Exception as e:
        raise Exception(f"Could not create Google Drive service: {e}")

def get_image_collection(target_date, aoi):
    """Finds the best Sentinel-2 images in a date range for a given AOI."""
    start_date = (target_date - timedelta(days=15)).strftime('%Y-%m-%d')
    end_date = (target_date + timedelta(days=15)).strftime('%Y-%m-%d')
    collection = (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
                  .filterBounds(aoi)
                  .filterDate(start_date, end_date)
                  .sort('CLOUDY_PIXEL_PERCENTAGE'))
    return collection.first()

def mask_s2_clouds(image):
    """Masks clouds and shadows from a Sentinel-2 image."""
    scl = image.select('SCL')
    # SCL values to mask: 1=saturated/defective, 3=cloud shadows, 8=medium probability clouds, 9=high probability clouds, 10=cirrus
    mask = (scl.eq(1).Or(scl.eq(3)).Or(scl.eq(8)).Or(scl.eq(9)).Or(scl.eq(10))).Not()
    return image.updateMask(mask)

def export_and_download(image, aoi, drive_service, filename_prefix, temp_dir):
    """
    Exports a multi-band GeoTIFF from GEE to Google Drive, waits for completion, and downloads it.
    The exported image has a fixed dimension of 1024x1024 pixels and contains all bands needed for
    both U-Net (B4, B3, B2) and NDVI (B8, B4) processing.
    """
    if image is None:
        return None
        
    masked_image = mask_s2_clouds(image)

    # Check for valid pixels to prevent errors with fully occluded AOIs
    valid_pixels = masked_image.select('B4').reduceRegion(
        reducer=ee.Reducer.count(),
        geometry=aoi,
        scale=10,
        maxPixels=1e9
    ).get('B4').getInfo()
    
    if valid_pixels is None or valid_pixels == 0:
        return None # No valid pixels, so we cannot proceed

    # Define all bands for export: B4, B3, B2 for U-Net, and B8 for NDVI.
    # B4 is included in both, so we export it once.
    bands_to_export = ['B4', 'B3', 'B2', 'B8']
    
    # Resample all bands to a consistent 10m resolution before export for consistency.
    export_image = masked_image.select(bands_to_export).resample('bicubic').clip(aoi)
    
    # --- IMPORTANT CHANGE FOR UNET INFERENCE ---
    # Convert the 16-bit satellite imagery to a more standard 8-bit RGB image.
    # This also applies a simple visualization stretch, which helps with the "low light" issue.
    # We will export the full 4 bands, but with the first 3 (B4, B3, B2) scaled to 0-255.
    
    # Define a visualization function for the RGB bands (B4, B3, B2)
    # The min/max values are based on typical Sentinel-2 reflectances
    vis_params = {
        'bands': ['B4', 'B3', 'B2'],
        'min': 0,
        'max': 3000,  # A typical max value to stretch the contrast
        'gamma': 1.4  # A slight gamma adjustment for better visual appearance
    }
    
    # Create the RGB visualization image (3 bands)
    rgb_image = export_image.visualize(**vis_params)
    
    # Add the NIR band (B8) as a fourth band, scaled to 0-255 as well.
    # This keeps the original band data for the NDVI calculation.
    b8_image = export_image.select('B8').visualize(min=0, max=5000, palette=['black', 'white'])
    
    # Combine the RGB and NIR bands back into a single image for export.
    # The order will be B4, B3, B2 (as a visual RGB), and then B8.
    final_export_image = rgb_image.addBands(b8_image)

    # The 'dimensions' parameter is critical to enforce the 1024x1024 pixel size
    image_dimensions = '1024x1024'
    
    drive_folder = 'GEE_Image_Exports'
    export_task = ee.batch.Export.image.toDrive(
        image=final_export_image,
        description=f"Export_{filename_prefix}",
        folder=drive_folder,
        fileNamePrefix=filename_prefix,
        dimensions=image_dimensions,
        region=aoi.bounds(), 
        fileFormat='GeoTIFF', 
        maxPixels=1e13
    )
    export_task.start()

    # Wait for the task to complete
    while export_task.active():
        time.sleep(10)

    task_status = export_task.status()
    if task_status['state'] != 'COMPLETED':
        raise Exception(f"GEE export task failed: {task_status.get('error_message', 'No error message.')}")

    # Find the file in Google Drive and download it
    folder_query = f"mimeType='application/vnd.google-apps.folder' and name='{drive_folder}' and trashed=false"
    folder_response = drive_service.files().list(q=folder_query, spaces='drive', fields='files(id)').execute()
    
    if not folder_response.get('files'):
        raise Exception(f"Could not find Google Drive folder: '{drive_folder}'.")
    folder_id = folder_response.get('files')[0].get('id')

    filename = f"{filename_prefix}.tif"
    file_query = f"name='{filename}' and '{folder_id}' in parents and trashed=false"
    file_response = drive_service.files().list(q=file_query, spaces='drive', fields='files(id)').execute()
    
    if not file_response.get('files'):
        raise Exception(f"Could not find file '{filename}' in Drive folder '{drive_folder}'.")
    file_id = file_response.get('files')[0].get('id')
    
    request = drive_service.files().get_media(fileId=file_id)

    filepath = os.path.join(temp_dir, filename)
    with io.FileIO(filepath, 'wb') as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()

    return filepath

def main(geojson_str, start_date_str, end_date_str):
    """Main function to perform the full backend download workflow."""
    try:
        ee.Initialize(project='areaofinterest')
        drive_service = authenticate_gdrive()

        geojson_data = json.loads(geojson_str)
        aoi = ee.Geometry.Polygon(geojson_data['coordinates'])
        date_t1 = datetime.strptime(start_date_str, '%Y-%m-%d')
        date_t2 = datetime.strptime(end_date_str, '%Y-%m-%d')
        
        image_t1 = get_image_collection(date_t1, aoi)
        image_t2 = get_image_collection(date_t2, aoi)

        # Create the temp_downloads folder inside the processing directory if it doesn't exist
        temp_downloads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp_downloads')
        if not os.path.exists(temp_downloads_dir):
            os.makedirs(temp_downloads_dir)
        
        t1_path = export_and_download(image_t1, aoi, drive_service, 'image_t1', temp_downloads_dir)
        t2_path = export_and_download(image_t2, aoi, drive_service, 'image_t2', temp_downloads_dir)

        if not t1_path or not t2_path:
            raise Exception("Failed to download one or both images after cloud masking. The AOI may be fully occluded by clouds.")

        response = {
            "status": "success",
            "t1_path": t1_path,
            "t2_path": t2_path,
            "temp_dir": temp_downloads_dir
        }
        print(json.dumps(response))

    except ee.EEException as e:
        print(json.dumps({"status": "error", "message": f"Earth Engine Error: {e}"}), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"status": "error", "message": f"Processing Error: {e}"}), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(json.dumps({"status": "error", "message": "Missing command-line arguments."}), file=sys.stderr)
        sys.exit(1)
    
    geojson_str = sys.argv[1]
    start_date = sys.argv[2]
    end_date = sys.argv[3]

    main(geojson_str, start_date, end_date)



