import cv2
import numpy as np


def replace_original_image(original_image, target, mask, processed_pixels):
    original_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)

    # Ensure both images have the same shape
    if original_image.size == target.size:
        # Create a copy of the original image
        result_image = original_image.copy()

        # Replace the corresponding section in 'original_image' with the non-zero pixels from 'result'
        non_zero_indices = np.nonzero(mask)
        new_pixels = set(zip(non_zero_indices[0], non_zero_indices[1])) - processed_pixels
        rows, cols = zip(*new_pixels)
        result_image[rows, cols] = target[rows, cols]
        processed_pixels.update(new_pixels)
        result_image = cv2.cvtColor(result_image, cv2.COLOR_BGR2RGB)
        return result_image
    else:
        print("The original image and mask must have the same shape.")