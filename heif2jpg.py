"""CNDY's HEIC/HEIF to JPEG Conversion Tool

A precise and lightweight solution designed to convert HEIC/HEIF images to JPEG format.

By CNDY.

Git: https://github.com/CNDY1390/HEIF-to-JPG
"""

from PIL import Image, ImageCms
import numpy as np
from io import BytesIO
from pathlib import Path
from pillow_heif import register_heif_opener
import argparse


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


def convert(heif_path, output_path, is_p3_to_srgb, is_with_icc, is_with_exif, quality):
    if quality > 100 or quality < 1:
        raise ValueError("Quality should be between 1 and 100.")
    register_heif_opener()
    heif_path = Path(heif_path)
    if output_path is None:
        output_path = heif_path.with_suffix('.jpg')
    else:
        output_path = Path(output_path)
    image_info = Image.open(heif_path).info
    icc_data = image_info.get('icc_profile')
    exif_data = image_info.get("exif")
    try:
        # rgb_data = np.array(open_heif(heif_path))
        rgb_data = np.array(Image.open(heif_path))
        if heif_path.suffix.lower() == ".heic":
            pass
        if heif_path.suffix.lower() == ".heif":
            rgb_data = yuv_limited_to_full(rgb_data)
            if is_p3_to_srgb:
                rgb_data = p3_to_srgb(rgb_data, icc_data)
        img = Image.fromarray(rgb_data)
        if output_path.exists():
            raise FileExistsError("Output file already exists.")
        metadata = dict()
        if is_with_icc:
            metadata['icc_profile'] = icc_data
        if is_with_exif:
            metadata['exif'] = exif_data
        img.save(output_path, quality=quality, **metadata)
        print(f"Conversion completed: {output_path}")
    except Exception:
        raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Convert HEIF/HEIC images to JPEG')
    parser.add_argument('heif_path', type=str,
                        help='Path to input HEIF/HEIC file')
    parser.add_argument('-o', '--output', type=str,
                        default=None, help='Path to output JPEG file')
    parser.add_argument('--p3-to-srgb', action='store_true',
                        help='Convert P3 to sRGB color space')
    parser.add_argument('--no-icc', action='store_false',
                        dest='with_icc', help='Skip ICC profile')
    parser.add_argument('--no-exif', action='store_false',
                        dest='with_exif', help='Skip EXIF data')
    parser.add_argument('-q', '--quality', type=int,
                        default=100, help='JPEG quality (1-100)')

    args = parser.parse_args()
    heif_path = args.heif_path
    output_path = args.output
    is_p3_to_srgb = args.p3_to_srgb
    is_with_icc = args.with_icc
    is_with_exif = args.with_exif
    quality = args.quality
    convert(heif_path, output_path, is_p3_to_srgb,
            is_with_icc, is_with_exif, quality)
