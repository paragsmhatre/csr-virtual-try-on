# Copyright 2023 Google LLC. This software is provided as-is, without warranty
# or representation for any use or purpose. Your use of it is subject to your
# agreement with Google
"""Apply masking"""
import numpy as np
import cv2
import imutils


# def merge_pixel(pattern_pixel, mask_pixel, contrast):
#     merged_pixel = pattern_pixel * ((mask_pixel / 255) * contrast)
#     merged_pixel = [float(i) for i in merged_pixel]
#     merged_pixel = np.clip(merged_pixel, 0, 255)
#     return merged_pixel


# def itterate_pixel(pattern_array, mask_array, contrast):
#     merged_image = []
#     for index, pattern_row in enumerate(pattern_array):
#         merged_image_col = []
#         for row_index, pattern_cell in enumerate(pattern_row):
#             merged_image_pixel = merge_pixel(pattern_cell,
#                                              mask_array[index][row_index], contrast)
#             merged_image_col.append(merged_image_pixel)
#         merged_image.append(merged_image_col)
#     return np.array(merged_image)

def iterate_pixel(pattern_array, mask_array, contrast):

    merged_image = pattern_array * (mask_array / 255.0) * contrast
    merged_image = np.clip(merged_image, 0, 255).astype(float)

    return merged_image


def apply_light_masking(cropped_image, pattern_image, base_image, contrast):
    # repeat the pattern
    pattern_image = cv2.cvtColor(pattern_image, cv2.COLOR_BGR2RGB)
    pattern_image = cv2.resize(pattern_image,
                               (base_image.shape[1], base_image.shape[0]))
    # TODO: Generalize the logic
    # light_mask = cropped_image - np.max(cropped_image)
    light_mask = cropped_image
    final_output = iterate_pixel(pattern_image, light_mask, contrast)
    result = final_output.astype('int')
    return result


# def apply_light_masking(cropped_image, pattern_image, base_image, contrast, config, segment_name):
#     # repeat the pattern
#     pattern_image = cv2.cvtColor(pattern_image, cv2.COLOR_BGR2RGB)
#     pattern_image = cv2.resize(pattern_image,
#                                (base_image.shape[1], base_image.shape[0]))
#     segment_config = config[segment_name]
#     if len(segment_config) != 0:
#         elevation = segment_config["elevation"]
#         angle = segment_config["angle"]
#         pattern_image = rotate_elevate_pattern(elevation, angle, pattern_image)
#
#     # light_mask = cropped_image - np.max(cropped_image)
#     final_output = itterate_pixel(pattern_image, cropped_image, contrast)
#     result = final_output.astype('int')
#     return result


def apply_light_masking_hsv(cropped_image, pattern_image, base_image, is_dark):
    # repeat the pattern
    pattern_image = cv2.cvtColor(pattern_image, cv2.COLOR_RGB2HSV)

    base_image = cv2.cvtColor(base_image, cv2.COLOR_RGB2HSV)
    pattern_image = cv2.resize(pattern_image,
                               (base_image.shape[1], base_image.shape[0]))
    mask = cropped_image[:, :, 2]

    mean_brightness = np.mean(pattern_image[:, :, 2])

    if is_dark:
        print('DARK')
        pattern_image[:, :, 2] = mask + mean_brightness.astype('float32')
    else:
        print('LIGHT')
        pattern_image[:, :, 2] = mask

    result = cv2.cvtColor(pattern_image, cv2.COLOR_HSV2BGR)
    return result
