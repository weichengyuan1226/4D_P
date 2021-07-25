## License: Apache 2.0. See LICENSE file in root directory.
## Copyright(c) 2015-2017 Intel Corporation. All Rights Reserved.

###############################################
##      Open CV and Numpy integration        ##
###############################################

import pyrealsense2 as rs
import numpy as np
import cv2

def depth_preview():

    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    colorizer = rs.colorizer()

    pipeline.start(config)


    while True:
        
        # Wait for a coherent pair of frames: depth and color
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        
        ### POST PROCESSING FILTERS ###
        ##DECLARE FILTERS
        #Threshold filter
        threshold = rs.threshold_filter(min_dist = 0.15, max_dist = 2)
        #Decimation filter
        decimation = rs.decimation_filter()
        decimation.set_option(rs.option.filter_magnitude, 2)
        #Spatial filter
        spatial = rs.spatial_filter()
        spatial.set_option(rs.option.filter_magnitude, 1)#Filtering itterations from 1.000 to 5.000
        spatial.set_option(rs.option.filter_smooth_alpha, 1)
        spatial.set_option(rs.option.filter_smooth_delta, 3)# 8 is good
        spatial.set_option(rs.option.holes_fill, 2)
        #Temporal Filter
        temporal = rs.temporal_filter()
        temporal.set_option(rs.option.filter_smooth_alpha, 0.2)
        temporal.set_option(rs.option.filter_smooth_delta, 100)

        depth_to_disparity = rs.disparity_transform(True)
        disparity_to_depth = rs.disparity_transform(True)
    

        #Apply filters
        # depth_frame = frames
        depth_frame = threshold.process(depth_frame)
        depth_frame = temporal.process(depth_frame)
        depth_frame = decimation.process(depth_frame)
        depth_frame = spatial.process(depth_frame)
        
        # Convert images to numpy arrays
        depth_image = np.asanyarray(depth_frame.get_data())
        

        # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
        #depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
        
        #Realsense Colorizer process
        colorized_depth = np.asanyarray(colorizer.colorize(depth_frame).get_data())
        
        # Stack both images horizontally
        images = colorized_depth

        # Show images
        cv2.namedWindow('RealSense', cv2.WINDOW_NORMAL)
        cv2.imshow('RealSense', images)
        k = cv2.waitKey(1)
        if k == 27:         # wait for ESC key to exit
            cv2.destroyAllWindows()
            pipeline.stop()

depth_preview()