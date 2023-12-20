# Virtual Try On

```
python3 main.py --input_image "./data/template1/template-1.jpg" --pattern_image "./data/template1/pattern7.jpeg" --input_json "./data/template1/template-1.json" --output_image "./data/template1/template-1-result.jpg"  --contrast 1.5
```


```
python3 main.py --input_image "./data/template1/template-1.jpg" --pattern_image "./data/template1/pattern6.jpg" --input_json "./data/template1/template-1.json" --output_image "./data/template1/template-2-result.jpg"  --contrast 1.0
```


```
python3 main.py --input_image "./data/template1/template-1.jpg" --pattern_image "./data/template1/pattern8.jpeg" --input_json "./data/template1/template-1.json" --output_image "./data/template1/template-3-result.jpg"  --contrast 1.0
```
# Yellow pattern
```
python3 main.py --input_image "./data/template1/template-1.jpg" --pattern_image "./data/template1/pattern9.jpeg" --input_json "./data/template1/template-1.json" --output_image "./data/template1/template-4-result.jpg" --contrast 1.1
```

# Checks patten
```
python3 main.py --input_image "./data/template1/template-1.jpg" --pattern_image "./data/template1/pattern10.jpeg" --input_json "./data/template1/template-1.json" --output_image "./data/template1/template-5-result.jpg" --contrast 1.06
```

# End-to-End
```shell
python3 main.py --input_image_path "./data/template2/original-white-saree.jpg" --pattern_image "./data/template1/pattern6.jpg" --segment_dir "./data/template2/plain-white-saree-segments" --output_image "./data/template2/template-2-result.jpg"  --contrast 1.0
```

# End-to-End multiple patterns
python3 main.py \
--input_image "./data/white-saree/enlarge_image__4_.png" \
--pattern_image_base_path "./data/raw_images" \
--segment_dir "./data/white-saree/segmentations" \
--output_dir "./data/output_results"  \
--contrast 1.0

# ImageGen
python3 main.py \
--input_image "./data/white-saree/enlarge_image__4_.png" \
--pattern_image_base_path "./data/raw_images_v2" \
--segment_dir "./data/white-saree/segmentations" \
--output_dir "./output_results_v3"  \
--contrast 1.0 \
--background_image_prompt "Create a background image that showcases a minimalist and modern living room, with our bookshelf subtly complementing the aesthetic. Use warm and natural lighting to emphasize the shelf's practicality and versatility. The camera angle should be a wide shot to capture the bookshelf in its entirety."

# Rotate Elevate ImageGen
python3 main.py \
--input_image "./data/white-saree/enlarge_image__4_.png" \
--pattern_image_base_path "./data/raw_images_v2" \
--segment_dir "./data/white-saree/segmentations" \
--output_dir "./output_results_v3"  \
--contrast 1.0 \
--config_json_path "./data/template2/config.json" \
--masking_json_path "./config/warping_points.json"
--background_image_prompt "Create a soft focus 4k HDR beautiful taken by a
professional photographer background image that showcases a minimalist and modern indian marriage hall, with our indian marriage hall subtly complementing the aesthetic. Use warm and natural lighting to emphasize the shelf's practicality and versatility. The camera angle should be a close shot to capture the indian marriage hall in its entirety. Make sure the background image is realistic."
