import cv2
import numpy as np
from rembg import remove


def get_background_mask(input_path, output_path):
    with open(input_path, 'rb') as i:
        with open(output_path, 'wb') as o:
            inp = i.read()
            output = remove(inp, only_mask=True)
            o.write(output)
    mask_image = cv2.imread(output_path, cv2.IMREAD_GRAYSCALE)
    inverted_mask = np.bitwise_not(mask_image)
    cv2.imwrite(output_path, inverted_mask)

def remove_background(input_path, output_path):
    with open(input_path, 'rb') as i:
        with open(output_path, 'wb') as o:
            inp = i.read()
            output = remove(inp)
            o.write(output)