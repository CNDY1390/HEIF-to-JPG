"""CNDY’s HEIC/HEIF to JPEG Conversion Tool

A precise and lightweight solution designed to convert HEIC/HEIF images to JPEG format.

By CNDY.

Git: https://github.com/CNDY1390/HEIF-to-JPG
"""

from PIL import Image, ImageCms
import numpy as np
from io import BytesIO
import os
from pillow_heif import register_heif_opener


def yuv_limited_to_full(rgb_data):
    rgb_data = rgb_data.astype(np.float32)
    rgb_data = (rgb_data - 16) * (255 / (235 - 16))
    rgb_data = np.clip(rgb_data, 0, 255).astype(np.uint8)
    return np.array(rgb_data)


def p3_to_srgb(rgb_data, icc_data):
    # input_profile = ImageCms.getOpenProfile(icc_profile_path)
    input_profile = ImageCms.ImageCmsProfile(BytesIO(icc_data))
    output_profile = ImageCms.createProfile('sRGB')
    transform = ImageCms.buildTransformFromOpenProfiles(
        input_profile, output_profile,
        'RGB', 'RGB'
    )
    rgb_data = ImageCms.applyTransform(Image.fromarray(rgb_data), transform)
    return np.array(rgb_data)


def main(heif_path, is_p3_to_srgb=False, is_with_icc=True, is_with_exif=True, quality=100):
    register_heif_opener()
    output_path = f"{heif_path[:-5]}.jpg"
    image_info = Image.open(heif_path).info
    icc_data = image_info.get('icc_profile')
    exif_data = image_info.get("exif")
    try:
        # rgb_data = np.array(open_heif(heif_path))
        rgb_data = np.array(Image.open(heif_path))
        if heif_path.lower().endswith(".heic"):
            pass
        if heif_path.lower().endswith(".heif"):
            rgb_data = yuv_limited_to_full(rgb_data)
            if is_p3_to_srgb:
                rgb_data = p3_to_srgb(rgb_data, icc_data)
        img = Image.fromarray(rgb_data)
        if os.path.exists(output_path):
            raise FileExistsError("Output file already exists.")
        if is_with_icc:
            # icc_data = ImageCms.getOpenProfile(icc_profile_path).tobytes()
            if is_with_exif:
                img.save(output_path, quality=quality,
                         icc_profile=icc_data, exif=exif_data)
            else:
                img.save(output_path, quality=quality, icc_profile=icc_data)
        else:
            if is_with_exif:
                img.save(output_path, quality=quality, exif=exif_data)
            else:
                img.save(output_path, quality=quality)
        print(f"Conversion completed: {output_path}")
    except Exception:
        raise


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    heif_path = "your_heif_name.HEIF"
    is_p3_to_srgb = False
    is_with_icc = True
    is_with_exif = True
    quality = 100
    main(heif_path, is_p3_to_srgb,
         is_with_icc, is_with_exif, quality)
