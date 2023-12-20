#!/bin/bash

source env.sh

#if [ "$1" == "" ]; then
#  echo "Error: "
#  exit 1
#fi

python3 main.py \
--input_image $INPUT_IMAGE \
--pattern_image_base_path $PATTERN_IMAGE_BASE_PATH \
--segment_dir $SEGMENT_DIR \
--output_dir $OUTPUT_DIR  \
--contrast $CONTRAST \
--masking_json_path $MASKING_JSON_PATH \
--background_image_prompt "$BACKGROUND_IMAGE_PROMPT" \
