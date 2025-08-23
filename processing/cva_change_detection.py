import sys
import json
import os
import rasterio
import numpy as np

def read_bands(image_path, bands):
    """
    Reads a specified list of bands from a local GeoTIFF file.
    Args:
        image_path (str): Path to the GeoTIFF file.
        bands (list): A list of 1-based band indices to read.
    
    Returns:
        tuple: A tuple containing a stacked numpy array of the bands, 
               and metadata for writing a new file (transform, crs, width, height).
    """
    try:
        with rasterio.open(image_path) as src:
            # Read the specified bands and stack them into a single array
            stacked_bands = np.stack([src.read(band) for band in bands], axis=-1)
            return stacked_bands, src.transform, src.crs, src.width, src.height
    except rasterio.errors.RasterioIOError as e:
        raise ValueError(f"Could not open or read GeoTIFF file: {image_path}. Error: {e}")


def calculate_cva(t1_bands, t2_bands):
    """
    Calculates the Change Vector Analysis (CVA) magnitude image.
    Args:
        t1_bands (np.array): Stacked numpy array of bands for the first image.
        t2_bands (np.array): Stacked numpy array of bands for the second image.
    
    Returns:
        np.array: A 2D numpy array representing the CVA magnitude for each pixel.
    """
    # Ensure arrays have the same shape
    if t1_bands.shape != t2_bands.shape:
        raise ValueError("Input images for CVA must have the same dimensions.")
    
    # Calculate the difference vector for each pixel
    # np.seterr ignores potential warnings during calculation
    np.seterr(divide='ignore', invalid='ignore')
    difference_vector = t2_bands.astype(float) - t1_bands.astype(float)

    # Calculate the magnitude of the change vector for each pixel
    # This is the Euclidean distance in the multi-spectral space
    cva_magnitude = np.sqrt(np.sum(difference_vector**2, axis=-1))

    return cva_magnitude


def main(t1_path, t2_path, threshold):
    """Performs CVA change detection on local GeoTIFF files."""
    try:
        # Define the bands to use for CVA. Sentinel-2 bands are a good choice.
        # B2=Blue, B3=Green, B4=Red, B8=NIR
        # Using a fixed list here, but in a robust system this would be dynamic.
        bands_to_use = [2, 3, 4, 8]
        
        # Read the specified bands from both images
        t1_bands, _, _, _, _ = read_bands(t1_path, bands_to_use)
        t2_bands, transform, crs, width, height = read_bands(t2_path, bands_to_use)
        
        # Calculate the CVA magnitude
        cva_magnitude = calculate_cva(t1_bands, t2_bands)
        
        # Apply the threshold to find pixels with significant change
        change_mask = np.where(cva_magnitude > threshold, 1, 0)

        # Calculate areas (assuming a 10m scale from Sentinel-2)
        pixel_area_sqm = 10 * 10
        change_area_sqm = np.sum(change_mask) * pixel_area_sqm
        change_area_ha = change_area_sqm / 10000

        total_pixels = width * height
        total_aoi_area_ha = (total_pixels * pixel_area_sqm) / 10000
        
        percentage_change = (change_area_ha / total_aoi_area_ha) * 100
        
        response = {
            "status": "success",
            "summary": {
                "method": "Change Vector Analysis (CVA)",
                "bands_used": bands_to_use,
                "total_aoi_area_ha": total_aoi_area_ha,
                "total_change_area_ha": change_area_ha,
                "percentage_change": percentage_change
            }
        }
        
        print(json.dumps(response, indent=4))

    except ValueError as ve:
        response = {"status": "error", "message": f"CVA Processing Error: {ve}"}
        print(json.dumps(response, indent=4), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        response = {"status": "error", "message": f"An unexpected error occurred: {e}"}
        print(json.dumps(response, indent=4), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 4:
        response = {"status": "error", "message": "Missing command-line arguments (t1_path, t2_path, threshold)."}
        print(json.dumps(response, indent=4), file=sys.stderr)
        sys.exit(1)
    
    t1_path = sys.argv[1]
    t2_path = sys.argv[2]
    
    try:
        threshold = float(sys.argv[3])
    except ValueError:
        response = {"status": "error", "message": "Threshold must be a valid number."}
        print(json.dumps(response, indent=4), file=sys.stderr)
        sys.exit(1)
        
    main(t1_path, t2_path, threshold)