#!/bin/sh

export PROJECT="meesho-vto-thp-1023"
export REGION="us-central1"
export ZONE="us-central1-a"

export INPUT_IMAGE="./data/white-saree/enlarge_image__4_.png"
export PATTERN_IMAGE_BASE_PATH="./data/raw_images_v3"
export SEGMENT_DIR="./data/white-saree/segmentations_v3"
export MASKING_JSON_PATH="./config/warping_points.json"
export OUTPUT_DIR="./../vto-output/output_results_v6"
export CONTRAST="1.0"
export BACKGROUND_IMAGE_PROMPT="Create a soft focus 4k HDR beautiful taken by a
professional photographer background. Create a background image that showcases a minimalist and modern living room, with our bookshelf subtly complementing the aesthetic. Use warm and natural lighting to emphasize the shelf's practicality and versatility. The camera angle should be a close shot to capture the bookshelf in its entirety."
