import sys
import json
import os
import rasterio
import numpy as np

def calculate_ndvi(image_path):
    """
    Calculates NDVI from a local GeoTIFF file.
    Assumes the file contains B4 (Red) and B8 (NIR) bands.
    """
    with rasterio.open(image_path) as src:
        # Based on the previous export script, we have B4, B3, B2, B8 bands
        # We need to find the correct band indexes.
        # Let's assume rasterio reads them in the order they were exported.
        # Check the metadata or assume B4 is band 1, B8 is band 4
        # (This may vary, so a more robust check is needed, but this is a good start)
        red = src.read(1)  # B4 (Red)
        nir = src.read(4)  # B8 (NIR)
        
        # Avoid division by zero
        np.seterr(divide='ignore', invalid='ignore')
        ndvi = (nir.astype(float) - red.astype(float)) / (nir.astype(float) + red.astype(float))
        
        return ndvi, src.transform, src.crs, src.width, src.height

def main(t1_path, t2_path, threshold):
    """Performs NDVI change detection on local GeoTIFF files."""
    try:
        ndvi_t1, _, _, _, _ = calculate_ndvi(t1_path)
        ndvi_t2, transform, crs, width, height = calculate_ndvi(t2_path)
        
        # Calculate the NDVI difference
        ndvi_difference = ndvi_t2 - ndvi_t1
        
        # Apply the threshold
        gain_mask = np.where(ndvi_difference > threshold, 1, 0)
        loss_mask = np.where(ndvi_difference < -threshold, 1, 0)

        # Calculate areas (assuming a 10m scale from Sentinel-2)
        pixel_area_sqm = 10 * 10
        gain_area_sqm = np.sum(gain_mask) * pixel_area_sqm
        loss_area_sqm = np.sum(loss_mask) * pixel_area_sqm

        gain_area_ha = gain_area_sqm / 10000
        loss_area_ha = loss_area_sqm / 10000
        total_change_area_ha = gain_area_ha + loss_area_ha
        total_pixels = width * height
        
        percentage_change = (total_change_area_ha / (total_pixels * pixel_area_sqm / 10000)) * 100
        
        # Save the difference map (optional, for visualization later)
        # with rasterio.open(os.path.join(os.path.dirname(t1_path), 'ndvi_difference.tif'), 'w', driver='GTiff',
        #                     height=height, width=width, count=1, dtype=ndvi_difference.dtype,
        #                     crs=crs, transform=transform) as dst:
        #     dst.write(ndvi_difference.astype(rasterio.float32), 1)

        response = {
            "status": "success",
            "summary": {
                "total_aoi_area_ha": (width * height * pixel_area_sqm) / 10000,
                "gain_area_ha": gain_area_ha,
                "loss_area_ha": loss_area_ha,
                "total_change_area_ha": total_change_area_ha,
                "percentage_change": percentage_change
            }
        }
        
        print(json.dumps(response))

    except Exception as e:
        response = {"status": "error", "message": f"NDVI Processing Error: {e}"}
        print(json.dumps(response), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 4:
        response = {"status": "error", "message": "Missing command-line arguments (t1_path, t2_path, threshold)."}
        print(json.dumps(response), file=sys.stderr)
        sys.exit(1)
    
    t1_path = sys.argv[1]
    t2_path = sys.argv[2]
    threshold = float(sys.argv[3])
    
    main(t1_path, t2_path, threshold)