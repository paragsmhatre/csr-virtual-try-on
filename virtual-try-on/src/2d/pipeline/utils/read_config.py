# Copyright 2023 Google LLC. This software is provided as-is, without warranty
# or representation for any use or purpose. Your use of it is subject to your
# agreement with Google
"""Load segmentation from json exported from label studio"""
import json
from collections import defaultdict
import pandas

def read_config(config_path):
    label_studio_data = json.load(open(config_path, encoding='UTF-8'))
    return label_studio_data


def load_json(path,image_size):
    # Load Lable Studio Annotated Segment
    lable_studio_data=json.load(open(path,encoding='UTF-8'))
    segments=lable_studio_data[0]['annotations'][0]["result"]
    segments_points={}
    data=defaultdict(list)
    for segment in segments:
        segment_key=f"{segment['value']['keypointlabels'][0]}"
        x_point=segment['value']['x']
        y_point=segment['value']['y']
        if segment_key not in segments_points:
            data["segment"].append(segment_key)
            data["x_point"].append(int(x_point*(image_size[1]/100)))
            data["y_point"].append(int(y_point*(image_size[0]/100)))
    segment_points_df=pandas.DataFrame(data=data)
    #print("segments_points",segment_points_df)
    return segment_points_df



def load_manual_warping_points(path):
    lable_studio_data = json.load(open(path, encoding='UTF-8'))
    return lable_studio_data
