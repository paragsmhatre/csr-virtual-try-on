import cv2
import numpy as np
from PIL import Image
from img2texture import image_to_seamless


def overlay_and_blend(
        image,
        pct=0.1,
        xrepeats=2,
        yrepeats=1,
):
    """Creates overlay and blending.

    horizontally and vertically as required.
    """
    pil_pattern = Image.fromarray(image)
    pil_output = image_to_seamless(pil_pattern, overlap=pct)

    xfact = 1
    yfact = 1

    open_cv_image = np.array(pil_output)

    # simple tiling
    reduced = cv2.resize(open_cv_image, (0, 0), fx=xfact, fy=yfact, interpolation=cv2.INTER_AREA)
    simple_tiled_overlayed = cv2.repeat(reduced, yrepeats, xrepeats)
    return simple_tiled_overlayed


def get_reconstructed_sari(
        left,  # sari body img.
        right,  # pallu img.
        pct1=0.1,  # overlay percentage for body
        pct2=0.1,  # overlay percentage for body and pallu
):
    """This function takes two different patterns as input.

    Both patterns are horizontally blended with an overlay of
    given percentage value.
    """

    # make sure that vertical overlay doesn't affect the output,
    # attaching dummy image to take care of that
    topx = left[:int(left.shape[0] * (pct1)), :]
    new_left = np.vstack([left, topx])

    # making sari body two times.
    double_left = overlay_and_blend(new_left, pct1)

    # double body and pallu should have same height
    max_h = max(
        double_left.shape[0],
        right.shape[0],
    )
    double_left = cv2.resize(double_left, (double_left.shape[1], max_h))
    right = cv2.resize(right, (right.shape[1], max_h))

    # removing effects of vertical overlay
    topy = double_left[:int(double_left.shape[0] * pct2), :]
    new_double_left = np.vstack([double_left, topy])

    topz = right[:int(right.shape[0] * pct2), :]
    new_right = np.vstack([right, topz])

    #print(new_double_left.shape, new_right.shape)

    # blend in opposite direction
    blended = overlay_and_blend(
        np.hstack([new_right, new_double_left]),
        pct=pct2,
    )

    # now crop extra part from both sides
    new_width = new_double_left.shape[1] + new_right.shape[1]
    new_height = new_double_left.shape[0]

    # creating offsets
    offset1 = new_right.shape[1]
    offset2 = new_double_left.shape[1] - int(new_width * pct2)
    offset3 = int(new_height * pct2) // 2

    # getting final image
    final_sari = blended[offset3:, offset1:-offset2]

    return final_sari


def split_reconstructed_image(image,type, split_ratio=0.6):
    height, width, _ = image.shape

    # Calculate the split point
    split_point = int(split_ratio * width)

    # Split the image
    if type=="pallu":
        segment = image[:, split_point:]
        segment = cv2.rotate(segment, cv2.ROTATE_90_CLOCKWISE)
    else:
        segment = image[:, :split_point]
    

    return segment
