"""CNDY’s HEIC/HEIF to JPEG Conversion Tool

A precise and lightweight solution designed to convert HEIC/HEIF images to JPEG format.

By CNDY.

Git: https://github.com/CNDY1390/HEIF-to-JPG
"""

from PIL import Image, ImageCms
import numpy as np
import os
from pillow_heif import register_heif_opener, open_heif
os.chdir(os.path.dirname(os.path.abspath(__file__)))
register_heif_opener()


def yuv_limited_to_full(rgb_data):
    rgb_data = rgb_data.astype(np.float32)
    rgb_data = (rgb_data - 16) * (255 / (235 - 16))
    rgb_data = np.clip(rgb_data, 0, 255).astype(np.uint8)
    return np.array(rgb_data)


def p3_to_srgb(rgb_data):
    global icc_profile_path
    input_profile = ImageCms.getOpenProfile(icc_profile_path)
    output_profile = ImageCms.createProfile('sRGB')
    transform = ImageCms.buildTransformFromOpenProfiles(
        input_profile, output_profile,
        'RGB', 'RGB'
    )
    rgb_data = ImageCms.applyTransform(Image.fromarray(rgb_data), transform)
    return np.array(rgb_data)


def main(heif_path, is_p3_to_srgb=False, is_with_icc=True, icc_profile_path='mi_dci_p3.icc', quality=100):
    try:
        rgb_data = np.array(open_heif(heif_path))
        if heif_path.lower().endswith(".heic"):
            pass
        if heif_path.lower().endswith(".heif"):
            rgb_data = yuv_limited_to_full(rgb_data)
            if is_p3_to_srgb:
                rgb_data = p3_to_srgb(rgb_data)
        img = Image.fromarray(rgb_data)
        output_path = f"{heif_path[:-5]}.jpg"
        if os.path.exists(output_path):
            print(f"File already exists: {output_path}")
            return
        if is_with_icc:
            icc_data = ImageCms.getOpenProfile(icc_profile_path).tobytes()
            img.save(output_path, quality=quality, icc_profile=icc_data)
        else:
            img.save(output_path, quality=quality)
    except Exception as e:
        raise f"Error: {e}"


if __name__ == '__main__':
    heif_path = "your heif file path"
    is_p3_to_srgb = False
    is_with_icc = True
    icc_profile_path = 'mi_dci_p3.icc'
    quality = 100
    main(heif_path, is_p3_to_srgb,
         is_with_icc, icc_profile_path, quality)
