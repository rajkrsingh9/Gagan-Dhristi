# # unet_inference.py
# unet_inference.py

import os
import sys
import json
import torch
import torch.nn as nn
import numpy as np
import rasterio
from PIL import Image
import torchvision.transforms as transforms
import matplotlib.pyplot as plt

# ==============================================================================
# 1. MODEL ARCHITECTURE
# (Copied from your original scripts - no changes needed here)
# ==============================================================================

class ConvBlock(nn.Module):
    """A simple convolutional block with Conv2d, BatchNorm2d, and ReLU activation."""
    def __init__(self, in_channels, out_channels):
        super(ConvBlock, self).__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True)
        )
    def forward(self, x):
        return self.conv(x)

class SiameseUNet(nn.Module):
    """A Siamese U-Net for change detection."""
    def __init__(self, in_channels=3, out_channels=1):
        super(SiameseUNet, self).__init__()
        # Encoder for Image 1
        self.enc1_conv1 = ConvBlock(in_channels, 64)
        self.enc1_maxpool1 = nn.MaxPool2d(kernel_size=2, stride=2)
        self.enc1_conv2 = ConvBlock(64, 128)
        self.enc1_maxpool2 = nn.MaxPool2d(kernel_size=2, stride=2)
        self.enc1_conv3 = ConvBlock(128, 256)
        self.enc1_maxpool3 = nn.MaxPool2d(kernel_size=2, stride=2)
        self.enc1_conv4 = ConvBlock(256, 512)
        self.enc1_maxpool4 = nn.MaxPool2d(kernel_size=2, stride=2)

        # Encoder for Image 2
        self.enc2_conv1 = ConvBlock(in_channels, 64)
        self.enc2_maxpool1 = nn.MaxPool2d(kernel_size=2, stride=2)
        self.enc2_conv2 = ConvBlock(64, 128)
        self.enc2_maxpool2 = nn.MaxPool2d(kernel_size=2, stride=2)
        self.enc2_conv3 = ConvBlock(128, 256)
        self.enc2_maxpool3 = nn.MaxPool2d(kernel_size=2, stride=2)
        self.enc2_conv4 = ConvBlock(256, 512)
        self.enc2_maxpool4 = nn.MaxPool2d(kernel_size=2, stride=2)

        self.bottleneck = ConvBlock(512 * 2, 1024)

        # Decoder
        self.upconv4 = nn.ConvTranspose2d(1024, 512, kernel_size=2, stride=2)
        self.dec_conv4 = ConvBlock(512 + 512 + 512, 512)

        self.upconv3 = nn.ConvTranspose2d(512, 256, kernel_size=2, stride=2)
        self.dec_conv3 = ConvBlock(256 + 256 + 256, 256)

        self.upconv2 = nn.ConvTranspose2d(256, 128, kernel_size=2, stride=2)
        self.dec_conv2 = ConvBlock(128 + 128 + 128, 128)

        self.upconv1 = nn.ConvTranspose2d(128, 64, kernel_size=2, stride=2)
        self.dec_conv1 = ConvBlock(64 + 64 + 64, 64)

        self.final_conv = nn.Conv2d(64, out_channels, kernel_size=1)

    def forward(self, x1, x2):
        # Encoder 1
        s1_1 = self.enc1_conv1(x1)
        e1_1 = self.enc1_maxpool1(s1_1)
        s1_2 = self.enc1_conv2(e1_1)
        e1_2 = self.enc1_maxpool2(s1_2)
        s1_3 = self.enc1_conv3(e1_2)
        e1_3 = self.enc1_maxpool3(s1_3)
        s1_4 = self.enc1_conv4(e1_3)
        e1_4 = self.enc1_maxpool4(s1_4)

        # Encoder 2
        s2_1 = self.enc2_conv1(x2)
        e2_1 = self.enc2_maxpool1(s2_1)
        s2_2 = self.enc2_conv2(e2_1)
        e2_2 = self.enc2_maxpool2(s2_2)
        s2_3 = self.enc2_conv3(e2_2)
        e2_3 = self.enc2_maxpool3(s2_3)
        s2_4 = self.enc2_conv4(e2_3)
        e2_4 = self.enc2_maxpool4(s2_4)

        # Bottleneck (Feature Fusion)
        fused_bottleneck = self.bottleneck(torch.cat([e1_4, e2_4], dim=1))

        # Decoder with fused skip connections
        d4 = self.upconv4(fused_bottleneck)
        d4 = torch.cat([d4, s1_4, s2_4], dim=1)
        d4 = self.dec_conv4(d4)

        d3 = self.upconv3(d4)
        d3 = torch.cat([d3, s1_3, s2_3], dim=1)
        d3 = self.dec_conv3(d3)

        d2 = self.upconv2(d3)
        d2 = torch.cat([d2, s1_2, s2_2], dim=1)
        d2 = self.dec_conv2(d2)

        d1 = self.upconv1(d2)
        d1 = torch.cat([d1, s1_1, s2_1], dim=1)
        d1 = self.dec_conv1(d1)

        # Final output
        output = self.final_conv(d1)
        return output

def create_and_save_visualizations(original_t2, change_mask, output_dir, t2_filename):
    """
    Creates and saves a blended image and a change-only image as PNGs.
    """
    # Create the base filename without extension
    base_filename = os.path.splitext(t2_filename)[0]
    
    # 1. Blended Image (T2 with red overlay)
    blended_filename = f"{base_filename}_change_overlay.png"
    blended_path = os.path.join(output_dir, blended_filename)
    
    overlay = np.zeros_like(original_t2)
    overlay[change_mask == 1] = [255, 0, 0] # Red color for changes
    
    blended_image = Image.fromarray((original_t2 * 0.7 + overlay * 0.3).astype(np.uint8))
    blended_image.save(blended_path)
    
    # 2. Change-Only Image
    change_only_filename = f"{base_filename}_changes_only.png"
    change_only_path = os.path.join(output_dir, change_only_filename)
    
    change_only_image = np.zeros_like(original_t2)
    change_only_image[change_mask == 1] = [255, 0, 0]
    Image.fromarray(change_only_image.astype(np.uint8)).save(change_only_path)
    
    return blended_filename, change_only_filename


def main(t1_path, t2_path):
    try:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        MODEL_PATH = os.path.join(BASE_DIR, 'models', 'siamese_unet_levir_cd.pth')
        OUTPUT_DIR = os.path.join(BASE_DIR, 'temp_downloads')
        
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        if not os.path.exists(MODEL_PATH):
            response = {"status": "error", "message": f"Model file not found at '{MODEL_PATH}'."}
            print(json.dumps(response), file=sys.stderr)
            sys.exit(1)

        model = SiameseUNet(in_channels=3, out_channels=1)
        model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
        model.to(device)
        model.eval()
        
        transform_inference = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
        ])

        if not os.path.exists(t1_path) or not os.path.exists(t2_path):
            raise FileNotFoundError(f"Error: One or both input images not found. "
                                    f"Please check the paths: '{t1_path}' and '{t2_path}'.")

        with rasterio.open(t1_path) as src_t1:
            original_t1_array = src_t1.read()
            t1_transform = src_t1.transform
            t1_crs = src_t1.crs
        
        with rasterio.open(t2_path) as src_t2:
            original_t2_array = src_t2.read()
            
        original_t1_pil = Image.fromarray(np.transpose(original_t1_array[:3], (1, 2, 0)))
        original_t2_pil = Image.fromarray(np.transpose(original_t2_array[:3], (1, 2, 0)))
        
        input_t1 = transform_inference(original_t1_pil).unsqueeze(0).to(device)
        input_t2 = transform_inference(original_t2_pil).unsqueeze(0).to(device)

        with torch.no_grad():
            output = model(input_t1, input_t2)

        change_mask = (torch.sigmoid(output) > 0.5).float().squeeze(0).squeeze(0).cpu().numpy()

        # --- NEW: Visualization and Saving ---
        t2_filename = os.path.basename(t2_path)
        blended_filename, change_only_filename = create_and_save_visualizations(
            np.array(original_t2_pil), # Pass the original T2 image array
            change_mask, 
            OUTPUT_DIR,
            t2_filename
        )
        print(f"Blended image saved to: {os.path.join(OUTPUT_DIR, blended_filename)}")
        print(f"Change-only image saved to: {os.path.join(OUTPUT_DIR, change_only_filename)}")
        # --- End of New Code ---
        
        # --- 2.6. Save and report the results as a GeoTIFF ---
        total_pixels = change_mask.shape[0] * change_mask.shape[1]
        change_pixels_float = float(np.sum(change_mask))
        change_percentage_float = float((change_pixels_float / total_pixels) * 100)
        
        change_mask_filename = 'unet_change_mask.tif'
        change_mask_path = os.path.join(OUTPUT_DIR, change_mask_filename)

        profile = {
            'driver': 'GTiff',
            'height': change_mask.shape[0],
            'width': change_mask.shape[1],
            'count': 1,
            'dtype': rasterio.uint8,
            'crs': t1_crs,
            'transform': t1_transform,
            'compress': 'LZW'
        }
        with rasterio.open(change_mask_path, 'w', **profile) as dst:
            dst.write(change_mask.astype(rasterio.uint8), 1)

        print(f"Detected change: {change_percentage_float:.2f}%")
        print(f"Total change pixels: {int(change_pixels_float)}")
        print(f"Change mask saved to: {change_mask_path}")

        # --- 2.7. Send a JSON response to the backend ---
        response = {
            "status": "success",
            "message": "U-Net inference completed successfully.",
            "percentage_change": change_percentage_float,
            "total_change_pixels": int(change_pixels_float),
            "change_mask_path": change_mask_filename, # This is the GeoTIFF
            "change_overlay_png": blended_filename,    # New PNG for visualization
            "change_only_png": change_only_filename    # New PNG for visualization
        }
        print(json.dumps(response))

    except Exception as e:
        response = {"status": "error", "message": f"Processing Error: {e}"}
        print(json.dumps(response), file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        response = {"status": "error", "message": "Missing command-line arguments (t1_path, t2_path)."}
        print(json.dumps(response), file=sys.stderr)
        sys.exit(1)
    
    t1_path = sys.argv[1]
    t2_path = sys.argv[2]
    
    main(t1_path, t2_path)


# def main(t1_path, t2_path):
#     """
#     Main function to run the change detection inference on two images.
#     Takes image paths as arguments from the command line.
#     """
#     try:
#         BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        
#         # --- 2.1. Define paths and device ---
#         MODEL_PATH = os.path.join(BASE_DIR, 'models', 'siamese_unet_levir_cd.pth')
#         OUTPUT_DIR = os.path.join(BASE_DIR, 'temp_downloads')
        
#         device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
#         print(f"Using device: {device}")

#         # Ensure output directory exists
#         os.makedirs(OUTPUT_DIR, exist_ok=True)

#         # --- 2.2. Load the model ---
#         if not os.path.exists(MODEL_PATH):
#             response = {"status": "error", "message": f"Model file not found at '{MODEL_PATH}'."}
#             print(json.dumps(response), file=sys.stderr)
#             sys.exit(1)

#         model = SiameseUNet(in_channels=3, out_channels=1)
#         model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
#         model.to(device)
#         model.eval()
#         print("Trained model loaded successfully.")
        
#         # --- 2.3. Define preprocessing transforms ---
#         # These must be the same as the ones used during training!
#         transform_inference = transforms.Compose([
#             transforms.ToTensor(),
#             transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
#         ])

#         # --- 2.4. Load and preprocess images ---
#         print(f"Attempting to load images from: '{t1_path}' and '{t2_path}'")
        
#         if not os.path.exists(t1_path) or not os.path.exists(t2_path):
#             raise FileNotFoundError(f"Error: One or both input images not found. "
#                                     f"Please check the paths: '{t1_path}' and '{t2_path}'.")

#         # Load the images and their geospatial metadata using rasterio
#         with rasterio.open(t1_path) as src_t1:
#             # We assume the GeoTIFF contains a standard RGB visualization
#             # created by thegee_drive_download.py script.
#             original_t1_array = src_t1.read()
#             t1_transform = src_t1.transform
#             t1_crs = src_t1.crs
        
#         with rasterio.open(t2_path) as src_t2:
#             original_t2_array = src_t2.read()

#         # Convert the rasterio output (bands, height, width) to the PIL format (height, width, bands)
#         # and then to a PIL Image object.
#         # This is the key change to use the reliable `transforms`.
#         # The first 3 bands are R, G, B as exported by the gee_drive_download.py script.
#         image_t1_pil = Image.fromarray(np.transpose(original_t1_array[:3], (1, 2, 0)))
#         image_t2_pil = Image.fromarray(np.transpose(original_t2_array[:3], (1, 2, 0)))

#         # Preprocess and prepare for model
#         input_t1 = transform_inference(image_t1_pil).unsqueeze(0).to(device)
#         input_t2 = transform_inference(image_t2_pil).unsqueeze(0).to(device)

#         # --- 2.5. Run inference ---
#         with torch.no_grad():
#             output = model(input_t1, input_t2)

#         # Apply sigmoid and threshold to get the binary change mask
#         change_mask = (torch.sigmoid(output) > 0.5).float().squeeze(0).squeeze(0).cpu().numpy()

#         # --- 2.6. Save and report the results as a GeoTIFF ---
#         print("\n--- Inference Results ---")
#         total_pixels = change_mask.shape[0] * change_mask.shape[1]
#         change_pixels_float = float(np.sum(change_mask))
#         change_percentage_float = float((change_pixels_float / total_pixels) * 100)
        
#         change_mask_filename = 'unet_change_mask.tif'
#         change_mask_path = os.path.join(OUTPUT_DIR, change_mask_filename)

#         # Use rasterio to save the change mask with georeferencing from t1
#         profile = {
#             'driver': 'GTiff',
#             'height': change_mask.shape[0],
#             'width': change_mask.shape[1],
#             'count': 1,
#             'dtype': rasterio.uint8,
#             'crs': t1_crs,
#             'transform': t1_transform,
#             'compress': 'LZW'
#         }
#         with rasterio.open(change_mask_path, 'w', **profile) as dst:
#             dst.write(change_mask.astype(rasterio.uint8), 1)

#         print(f"Detected change: {change_percentage_float:.2f}%")
#         print(f"Total change pixels: {int(change_pixels_float)}")
#         print(f"Change mask saved to: {change_mask_path}")

#         # --- 2.7. Send a JSON response to the backend ---
#         response = {
#             "status": "success",
#             "message": "U-Net inference completed successfully.",
#             "percentage_change": change_percentage_float,
#             "total_change_pixels": int(change_pixels_float),
#             "change_mask_path": change_mask_filename
#         }
#         print(json.dumps(response))

#     except Exception as e:
#         response = {"status": "error", "message": f"Processing Error: {e}"}
#         print(json.dumps(response), file=sys.stderr)
#         sys.exit(1)


# if __name__ == '__main__':
#     if len(sys.argv) < 3:
#         response = {"status": "error", "message": "Missing command-line arguments (t1_path, t2_path)."}
#         print(json.dumps(response), file=sys.stderr)
#         sys.exit(1)
    
#     t1_path = sys.argv[1]
#     t2_path = sys.argv[2]
    
#     main(t1_path, t2_path)









