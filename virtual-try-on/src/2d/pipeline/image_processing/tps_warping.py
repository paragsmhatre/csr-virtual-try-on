import numpy as np
import cv2
import matplotlib.pyplot as plt

def WarpImage_TPS(source,target,img):
        tps = cv2.createThinPlateSplineShapeTransformer()
        source=source.reshape(-1,len(source),2)
        target=target.reshape(-1,len(target),2)
        matches=list()
        for i in range(0,len(source[0])):
                matches.append(cv2.DMatch(i,i,0))
        tps.estimateTransformation(target, source, matches)
        new_img = tps.warpImage(img)
        return new_img

import cv2
import numpy as np
import matplotlib.pyplot as plt
import math
from collections import defaultdict
import pandas

def get_start_end_points(segments_points_df,point_to_sort):
    segments_points_df=segments_points_df.sort_values(by=[point_to_sort])
    start_mask_point_df=segments_points_df.iloc[0]
    end_mask_point_df=segments_points_df.iloc[-1]
    start_mask_point=[start_mask_point_df["x_point"],start_mask_point_df["y_point"]]
    end_mask_point=[end_mask_point_df["x_point"],end_mask_point_df["y_point"]]
    return start_mask_point,end_mask_point

def map_points(point_row):
    mask_start=point_row["mask_mapped_points_start"]
    mask_end=point_row["mask_mapped_points_end"]
    
    mapped_points_start=point_row["mapped_points_start"]
    mapped_points_end=point_row["mapped_points_end"]
    
    point=[point_row["x_point"],point_row["y_point"]]
    
    if "-bottom" in point_row["segment"]:
        mapped_point=0
        mask_distance=mask_end[0]-mask_start[0]
        pattern_distance=mapped_points_end[0]-mapped_points_start[0]
        distance_from_start=point[0]-mask_start[0]
        mapped_point=int((pattern_distance/mask_distance)*distance_from_start)
        return [mapped_point,2160]
    if "-top" in point_row["segment"]:
        mapped_point=0
        mask_distance=mask_end[0]-mask_start[0]
        pattern_distance=mapped_points_end[0]-mapped_points_start[0]
        distance_from_start=point[0]-mask_start[0]
        mapped_point=int((pattern_distance/mask_distance)*distance_from_start)
        return [mapped_point,0]
    if "-left" in point_row["segment"]:
        mapped_point=0
        mask_distance=mask_end[1]-mask_start[1]
        pattern_distance=mapped_points_end[1]-mapped_points_start[1]
        distance_from_start=point[1]-mask_start[1]
        mapped_point=int((pattern_distance/mask_distance)*distance_from_start)
        return [0,mapped_point]
    if "-right" in point_row["segment"]:
        mapped_point=0
        mask_distance=mask_end[1]-mask_start[1]
        pattern_distance=mapped_points_end[1]-mapped_points_start[1]
        distance_from_start=point[1]-mask_start[1]
        mapped_point=int((pattern_distance/mask_distance)*distance_from_start)
        return [2160,mapped_point]
    
def tps_warp(pattern_image,segment_image,model_image,segments_points_df):
        im = cv2.resize(pattern_image,(2160,2160))
        # map points
        mapped_points_start=[]
        mapped_points_end=[]
        mask_mapped_points_start=[]
        mask_mapped_points_end=[]
        
        for index,row in segments_points_df.iterrows():
            if "-bottom" in row["segment"]:
                mapped_points_start.append([0,2160])
                mapped_points_end.append([2160,2160])
                segments_points_df_bottom=segments_points_df[segments_points_df['segment'].str.contains("bottom")]
                start_mask_point,end_mask_point=get_start_end_points(segments_points_df_bottom,"x_point")
                
                
            if "-top" in row["segment"]:
                mapped_points_start.append([0,0])
                mapped_points_end.append([2160,0])
                segments_points_df_bottom=segments_points_df[segments_points_df['segment'].str.contains("top")]
                start_mask_point,end_mask_point=get_start_end_points(segments_points_df_bottom,"x_point")
                
            if "-left" in row["segment"]:
                mapped_points_start.append([0,0])
                mapped_points_end.append([0,2160])
                segments_points_df_bottom=segments_points_df[segments_points_df['segment'].str.contains("left")]
                start_mask_point,end_mask_point=get_start_end_points(segments_points_df_bottom,"y_point")
                
            if "-right" in row["segment"]:
                mapped_points_start.append([2160,0])
                mapped_points_end.append([2160,2160])
                segments_points_df_bottom=segments_points_df[segments_points_df['segment'].str.contains("right")]
                start_mask_point,end_mask_point=get_start_end_points(segments_points_df_bottom,"y_point")
                
            mask_mapped_points_start.append(start_mask_point)
            mask_mapped_points_end.append(end_mask_point)
        segments_points_df["mapped_points_start"]=mapped_points_start
        segments_points_df["mapped_points_end"]=mapped_points_end
        segments_points_df["mask_mapped_points_start"]=mask_mapped_points_start
        segments_points_df["mask_mapped_points_end"]=mask_mapped_points_end
        
        # map points
        maped_points_list=[]
        for index,row in segments_points_df.iterrows():
            maped_point=map_points(row)
            maped_points_list.append(maped_point)
        segments_points_df["maped_points"]=maped_points_list
        source_points_list=[]
        distination_points_list=[]
        
        for index,segment_point in segments_points_df.iterrows():
            #if segment_point["maped_points"]==[0, 0] or segment_point["maped_points"]==[2160, 2160] or segment_point["maped_points"]==[0, 2160] or segment_point["maped_points"]==[2160, 0]:
                if segment_point["maped_points"] not in source_points_list and [segment_point["x_point"],segment_point["y_point"]] not in distination_points_list:
                    source_points_list.append(segment_point["maped_points"])
                    distination_points_list.append([segment_point["x_point"],segment_point["y_point"]])
            # im = cv2.circle(im, segment_point["source_point"], 10, [255,0,0], 10)
        Zp = np.array(source_points_list)
        Zs = np.array(distination_points_list)
        new_im = WarpImage_TPS(Zp, Zs, im)    
        # crop image
        x=0
        y=0
        h=2160
        w=1440
        new_im = new_im[y:y+h, x:x+w]
        return new_im