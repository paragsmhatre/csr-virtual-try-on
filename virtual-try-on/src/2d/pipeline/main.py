# Copyright 2023 Google LLC. This software is provided as-is, without warranty
# or representation for any use or purpose. Your use of it is subject to your
# agreement with Google
"""2D Stream Pipeline for Virtual Try On"""
import os
import argparse
import cv2
import numpy as np
import time
import json

from utils.read_config import read_config, load_manual_warping_points,load_json
from image_processing.masking import apply_light_masking, apply_light_masking_hsv
from image_processing.replace_image import replace_original_image
from image_processing.saree_reconstruction import get_reconstructed_sari, split_reconstructed_image
from image_processing.upscale_image import upscale
from image_processing.tps_warping import tps_warp
from image_gen.background_mask import get_background_mask,remove_background
from image_gen.call_image_gen import call_image_gen
import warnings
warnings.filterwarnings("ignore")

def concat_images(body, pallu, blouse, output_image):
    # Resize image1, image2, and image3 to have the same height as output_image
    height, width = output_image.shape[:2]
    image1 = cv2.resize(body, (width, height))
    image2 = cv2.resize(pallu, (width, height))
    image3 = cv2.resize(blouse, (width, height))

    # Concatenate images vertically on the left
    left_images = np.concatenate((image1, image2, image3), axis=0)
    left_images = cv2.resize(left_images, (output_image.shape[1], output_image.shape[0]))

    # Concatenate the left_images and image4 horizontally
    result_image = np.concatenate((left_images, output_image), axis=1)
    return result_image


def main(input_image_path,pattern_image_base_path,segment_dir_path,output_dir,contrast,background_image_prompt,masking_json_path,steps=["reconstruct","background_update","enhance_image"],body_zoom=20,pallu_zoom=60,blouse_zoom=30,top_half_body_zoom=30):
    
    # Original Image
    print("Step 1 : Load Original Image")
    original_image = cv2.imread(input_image_path)

    # Load warping config points
    segments_points_df=load_json(masking_json_path,original_image.shape)

    # Iterate over the patterns
    for pattern_name in os.listdir(pattern_image_base_path):
        if "reconstruct" in steps:
            start_time = time.time()
            if ".DS_Store" in pattern_name:
                continue
            processed_pixels = set()
            base_image = original_image

            print("Step 2: Reconstruct saree from pattern images")
            # Read the input pattern image
            input_pallu_img = cv2.imread(os.path.join(pattern_image_base_path, pattern_name, "pallu.png"))
            input_body_img = cv2.imread(os.path.join(pattern_image_base_path, pattern_name, "body.png"))
            input_blouse_image = cv2.imread(os.path.join(pattern_image_base_path, pattern_name, "blouse.png"))

            reconstructed_image = get_reconstructed_sari(
                left=input_body_img,
                right=input_pallu_img,
                pct1=0.02,
                pct2=0.01,
            )

            print(f"Step 3: Processing: {pattern_name}")
            # Split reconstructed saree to get the body and pallu images
            # Read config file for pattern zoom level
            zoom_level_config_file_path=os.path.join(pattern_image_base_path, pattern_name, "config.json")
            if os.path.exists(zoom_level_config_file_path):
                config_data=json.load(open(zoom_level_config_file_path))
                pallu_zoom=config_data["zoom_level"]["pallu_zoom"]
                body_zoom=config_data["zoom_level"]["body_zoom"]
                top_half_body_zoom=config_data["zoom_level"]["top_half_body_zoom"]
                blouse_zoom=config_data["zoom_level"]["blouse_zoom"]
            pallu_image = split_reconstructed_image(reconstructed_image, type="pallu",split_ratio=float(pallu_zoom)/100)
            body_image = split_reconstructed_image(reconstructed_image,type="body", split_ratio=float(body_zoom)/100)
            top_half_body_image = split_reconstructed_image(reconstructed_image,type="body", split_ratio=float(top_half_body_zoom)/100)

            # Step 1. Crop blouse_image center square - Rohit
            coroped_blouse_image=split_reconstructed_image(input_blouse_image,type="blouse", split_ratio=1.0)
            
            pattern_dict = {"body": body_image,
                            "tophalf":top_half_body_image,
                            "pallu": pallu_image,
                            "blouse": coroped_blouse_image} # step 2. 

            print("Step 4: Process saree segments")
            # Iterate over the segments
            for file in os.listdir(segment_dir_path):

                print(f"Step 4.1 : Load Segment: {file}")
                file_path = segment_dir_path + "/" + file
                cropped_image = cv2.imread(file_path)
                cropped_image = np.where(cropped_image > 0, 1, cropped_image)

                # Pleats
                print("Step 4.2 : Pre-process Segment")
                cropped_image_mask = cropped_image > 0
                cropped_image_processed = np.zeros_like(base_image)
                cropped_image_processed[cropped_image_mask] = base_image[cropped_image_mask]

                # Determine the segment type
                segment_type = None
                if 'bottomhalf' in file.lower():
                    segment_type = 'body'
                elif 'tophalf' in file.lower():
                    segment_type = 'tophalf'
                elif 'pallu' in file.lower():
                    segment_type = 'pallu'
                elif 'blouse' in file.lower():
                    segment_type = 'blouse'

                # Load specific patterns
                pattern_image = pattern_dict[segment_type]


                if 'blouse' in file.lower(): # Step 3 blouse TPS Warping
                    print("inside blouse processing...")
                    file_path = segment_dir_path + "/" + file
                    cropped_image_clean = cv2.imread(file_path)
                    #print("image", cropped_image_clean.shape)

                    segments_points_df_blouse=segments_points_df[segments_points_df['segment'].str.contains("blouse")]
                    pattern_image = tps_warp(pattern_image=pattern_image,
                                            segment_image=cropped_image_clean,
                                            model_image=base_image,
                                            segments_points_df=segments_points_df_blouse)
                    import matplotlib.pyplot as plt 
                    plt.imshow(pattern_image) 
                    # display that image 
                    plt.show()     
                elif 'pallu' in file.lower():
                    file_path = segment_dir_path + "/" + file
                    cropped_image_clean = cv2.imread(file_path)
                    #print("image", cropped_image_clean.shape)

                    segments_points_df_pallu=segments_points_df[segments_points_df['segment'].str.contains("pallu")]
                    pattern_image = tps_warp(pattern_image=pattern_image,
                                            segment_image=cropped_image_clean,
                                            model_image=base_image,
                                            segments_points_df=segments_points_df_pallu)
                elif "tophalf" in file.lower():
                    #print("inside tophalf")
                    file_path = segment_dir_path + "/" + file
                    cropped_image_clean = cv2.imread(file_path)
                    segments_points_df_tophalf=segments_points_df[segments_points_df['segment'].str.contains("tophalf")]
                    pattern_image = tps_warp(pattern_image=pattern_image,
                                            segment_image=cropped_image_clean,
                                            model_image=base_image,
                                            segments_points_df=segments_points_df_tophalf)
                elif "bottomhalf" in file.lower():
                    #print("inside bottomhalf")
                    file_path = segment_dir_path + "/" + file
                    cropped_image_clean = cv2.imread(file_path)
                    segments_points_df_bottomhalf=segments_points_df[segments_points_df['segment'].str.contains("bottomhalf")]
                    pattern_image = tps_warp(pattern_image=pattern_image,
                                            segment_image=cropped_image_clean,
                                            model_image=base_image,
                                            segments_points_df=segments_points_df_bottomhalf)
                else:
                    pattern_image = cv2.resize(pattern_image,
                                            (base_image.shape[1], base_image.shape[0]))

                # Check for dark or light mask:
                mean_brightness = np.mean(cv2.cvtColor(pattern_image, cv2.COLOR_RGB2HSV)[:, :, 2])
                is_dark = False if mean_brightness > 191 else True  # 3/4 of 255

                # Apply light mask
                print("Step 4.3 : Apply light mask")
                light_mask_image = apply_light_masking(cropped_image=cropped_image_processed,
                                                    pattern_image=pattern_image,
                                                    base_image=base_image,
                                                    contrast=contrast
                                                    )

                # # HSV
                # light_mask_image = apply_light_masking_hsv(cropped_image=cropped_image_processed,
                #                                            pattern_image=pattern_image,
                #                                            base_image=base_image,
                #                                            is_dark=is_dark)

                # plt.imshow(light_mask_image)
                # plt.show()

                # Replace Original
                print("Step 4.4 : Place over Original Image")
                base_image = replace_original_image(original_image=base_image,
                                                    target=light_mask_image,
                                                    mask=cropped_image_mask,
                                                    processed_pixels=processed_pixels
                                                    )

            # Write the final Image
            print("Step 5: Write the final images")
            os.makedirs(os.path.join(output_dir, pattern_name), exist_ok=True)
            cv2.imwrite(os.path.join(output_dir, pattern_name, f'{pattern_name}.png'), base_image)
            remove_background(os.path.join(output_dir, pattern_name, f'{pattern_name}.png'),os.path.join(output_dir, pattern_name, f'{pattern_name}_clean.png'))
            cv2.imwrite(os.path.join(output_dir, pattern_name, "reconstructed_image.png"), reconstructed_image)
            cv2.imwrite(os.path.join(output_dir, pattern_name, "body.png"), body_image)
            cv2.imwrite(os.path.join(output_dir, pattern_name, "pallu.png"), pallu_image)
            cv2.imwrite(os.path.join(output_dir, pattern_name, "blouse.png"), input_blouse_image)
            # Combine images
            # combine_image = concat_images(body_image, pallu_image, input_blouse_image, base_image)
            # cv2.imwrite(os.path.join(output_dir, pattern_name, f'{pattern_name}-combine.png'), combine_image)
            print("--- %s Saree Base Image generation seconds ---" % (time.time() - start_time))
        if "background_update" in steps:
            start_time = time.time()
            # Process background image with generative AI
            print("Step 6: Processing background with ImageGen")
            imagegen_output_dir = os.path.join(output_dir, pattern_name, "image_gen")
            os.makedirs(imagegen_output_dir, exist_ok=True)
            mask_output_image_path = os.path.join(output_dir, pattern_name, f'{pattern_name}-mask.png')
            get_background_mask(input_image_path, mask_output_image_path)

            # # Apply image background update with Imagegen
            call_image_gen(os.path.join(output_dir, pattern_name, f'{pattern_name}.png'),
                        mask_output_image_path,
                        imagegen_output_dir,
                        background_image_prompt)
            print("--- %s Image Gen Background Update seconds ---" % (time.time() - start_time))
        # if "enhance_image" in steps:
        #     start_time = time.time()
        #     print("Step 7: Upscale Image")
        #     upscale_image_output_dir = os.path.join(output_dir, pattern_name, "upscale")
        #     os.makedirs(upscale_image_output_dir, exist_ok=True)
        #     for image_gen_img in os.listdir(imagegen_output_dir):
        #         if '.DS_Store' in image_gen_img:
        #             continue
        #         upscale(image_path=os.path.join(imagegen_output_dir, image_gen_img),
        #                 output_path=os.path.join(upscale_image_output_dir, image_gen_img))
        #     print("--- %s Image Gen Upscaling seconds ---" % (time.time() - start_time))
        print(f"------ Completed: {pattern_name} ------\n")
        

    print("------Successfully Processed All the Patterns------")
    print("Completed")


if __name__ == "__main__":
    argParser = argparse.ArgumentParser()
    argParser.add_argument("-i", "--input_image_path",
                        help="Input model image path.", required=True)
    argParser.add_argument("-p", "--pattern_image_base_path",
                        help="Input pattern image dir path.", required=True)
    argParser.add_argument("-j", "--segment_dir",
                        help="Input directory containing segmentation images.", required=True)
    argParser.add_argument("-o", "--output_dir",
                        help="Output path.", required=True)
    argParser.add_argument("-c", "--contrast",
                        help="Contrast for shadows.", required=True, type=float)
    argParser.add_argument("-b", "--background_image_prompt",
                        help="Image gen background image prompt", required=True, type=str)
    argParser.add_argument("-mjp", "--masking_json_path",
                        help="Mask json path", required=True, type=str)

    args = argParser.parse_args()
    input_image_path = args.input_image_path
    pattern_image_base_path = args.pattern_image_base_path
    segment_dir_path = args.segment_dir
    output_dir = args.output_dir
    contrast = args.contrast
    background_image_prompt = args.background_image_prompt
    masking_json_path = args.masking_json_path

    
    main(input_image_path,pattern_image_base_path,segment_dir_path,output_dir,contrast,background_image_prompt,masking_json_path)
