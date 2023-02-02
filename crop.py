# -*- coding: utf-8 -*-

from collections import namedtuple
from PIL import Image
import math
import os
import sys
import io

def resize_images(source_dir, target_dir, threshold):
    filenames = os.listdir(source_dir)
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    for localname in filenames:
        filename = os.path.join(source_dir, localname)
        filesize = os.path.getsize(filename)

        vs = valid_suffix(filename)
        if not vs.flag:
            print("{} 不符合要求".format(filename))
            continue
        image = open(filename, "rb")
        with Image.open(image) as im:
            im_buf = io.BytesIO()
            try:
                im.save(im_buf, format="png")
            except:
                print(filename)
                continue
            with Image.open(im_buf) as im_png:
                width, height = im.size
                new_size = compress_strategy(threshold, filesize, width, height, "png")
                resized_im = im_png.resize((new_size.width, new_size.height))
                resized_im_buf = io.BytesIO()
                resized_im.save(resized_im_buf, format="png")
                resized_im_buf.seek(0)
                output_filename = filename.replace(source_dir, target_dir)
                suffix = output_filename.split(".")[-1]
                output_filename = output_filename.replace(suffix, "png")
                resized_im.save(output_filename)
                print(f"原始图片: {filename} 已压缩保存至 {output_filename}")

def valid_suffix(filename):
    ValidSuffix = namedtuple("ValidSuffix", ["flag", "suffix"])
    suffix = filename.split(".")[-1]
    valid_suffix = ["png", "jpg", "jpeg"]
    if suffix.lower() in valid_suffix:
        return ValidSuffix(True, suffix)
    return ValidSuffix(False, suffix)

def compress_strategy(threshold, filesize, width, height, suffix):
    ONE_K = 1024
    ONE_M = 1024 * 1024
    factor = 1
    if filesize <= 40 * ONE_K:
        # 图片小于等于40k则不做处理
        return convert_to_width_height(threshold * 400 * factor, filesize, width, height, suffix)
    if 40 * ONE_K < filesize <= 500 * ONE_K:
        return convert_to_width_height(threshold * 350 * factor, filesize, width, height, suffix)
    if 500 * ONE_K < filesize <= 1000 * ONE_K:
        return convert_to_width_height(threshold * 300 * factor, filesize, width, height, suffix)
    if 1000 * ONE_K < filesize <= 1500 * ONE_K:
        return convert_to_width_height(threshold * 250 * factor, filesize, width, height, suffix)
    if 1500 * ONE_K > filesize:
        return convert_to_width_height(threshold * (filesize / float(ONE_M) * 200) * factor, filesize, width, height, suffix)

    return convert_to_width_height(threshold * (filesize / float(ONE_M) * 150) * factor, filesize, width, height, suffix)

def convert_to_width_height(new_size, filesize, width, height, suffix):
    Size = namedtuple("Size", ["width", "height"])
    if width >= height:
        new_width = int(math.sqrt(new_size))
        new_height = int(new_width * height * 1.0 / width)
    else:
        new_height = int(math.sqrt(new_size))
        new_width = int(new_height * width * 1.0 / height)
    return Size(new_width, new_height)


if __name__ == "__main__":
    src = sys.argv[1]
    resize_images(src, "output", 128)
