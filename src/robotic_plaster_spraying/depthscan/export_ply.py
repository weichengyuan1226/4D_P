import pyrealsense2 as rs                 # Intel RealSense cross-platform open-source API
import sys, os
import numpy as np
import copy


print("Environment Ready")

def export (filename, mesh=True, pc=False):
    # Setup:
    pipe = rs.pipeline()    
    cfg = rs.config()

    #cfg.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    cfg.enable_stream(rs.stream.depth, 848, 480, rs.format.z16, 30)
    cfg.enable_stream(rs.stream.color, 848, 480, rs.format.rgb8, 30)
    profile = pipe.start(cfg)

    # pc = rs.pointcloud()

    align_to = rs.stream.color
    align = rs.align(align_to)

    # Skip 5 first frames to give the Auto-Exposure time to adjust
    for x in range(5):
        pipe.wait_for_frames()

    frames = []
    colors = []
    for x in range(15):
        frameset = pipe.wait_for_frames()
        aligned_frames = align.process(frameset)
        frames.append(aligned_frames.get_depth_frame())
        colors.append(aligned_frames.get_color_frame())
        # pc.map_to(colors)
        
    # print (pc)

    # Cleanup:
    pipe.stop()
    print("Frames Captured")

    ### POST PROCESSING FILTERS ###
    ##DECLARE FILTERS
    #Threshold filter
    threshold = rs.threshold_filter(min_dist = 0.15, max_dist = 3)
    #Decimation filter
    decimation = rs.decimation_filter()
    decimation.set_option(rs.option.filter_magnitude, 3)
    #Spatial filter
    spatial = rs.spatial_filter()
    spatial.set_option(rs.option.filter_magnitude, 1)
    spatial.set_option(rs.option.filter_smooth_alpha, 1)
    spatial.set_option(rs.option.filter_smooth_delta, 3)
    spatial.set_option(rs.option.holes_fill, 2)
    #Temporal Filter
    temporal = rs.temporal_filter()
    temporal.set_option(rs.option.filter_smooth_alpha, 0.2)
    temporal.set_option(rs.option.filter_smooth_delta, 100)
    #Hole filling
    hole_filling = rs.hole_filling_filter()
 
    depth_to_disparity = rs.disparity_transform(True)
    disparity_to_depth = rs.disparity_transform(True)


    #Apply filters
    depth_frames = []
    for i in range(15):    
        depth_frame = frameset
        depth_frame = threshold.process(depth_frame)
        depth_frame = temporal.process(depth_frame)
        depth_frame = decimation.process(depth_frame)
        depth_frame = spatial.process(depth_frame)
        # depth_frame = hole_filling.process(depth_frame)
        # points = pc.calculate(depth_frame)
        # depth_frames.append(depth_frame)


    # Create save_to_ply object

    if pc == True:
        #ply = rs.save_to_ply(os.path.abspath(os.path.join(path, 'data/ply/pc.ply')))
        # ply = rs.save_to_ply("C:\\Users\\sercan\\Documents\\GitHub\\intuitive-robotic-plastering\\data\\ply\\pc.ply")
        ply = rs.save_to_ply(filename)

        # Set options to the desired values
        # Generate a textual PLY with normals (mesh is already created by default)
        ply.set_option(rs.save_to_ply.option_ply_mesh, False)
        ply.set_option(rs.save_to_ply.option_ply_binary, False)
        ply.set_option(rs.save_to_ply.option_ply_normals, True)
        ply.set_option(rs.save_to_ply.option_ignore_color, False)
        print("Saving pointcloud...")
        # Apply the processing block to the frameset which contains the depth frame and the texture
        
        ply.process(depth_frame)
        print("Done")

    if mesh == True:
        #ply = rs.save_to_ply(os.path.abspath(os.path.join(path, 'data/ply/pc.ply')))
        # ply = rs.save_to_ply(os.path.abspath(os.path.join("C:\\Users\\sercan\\Documents\\GitHub\\intuitive-robotic-plastering\\data\\ply\\scan.ply")))
        ply = rs.save_to_ply(filename)

        ply.set_option(rs.save_to_ply.option_ply_mesh, True)
        ply.set_option(rs.save_to_ply.option_ply_binary, False)
        ply.set_option(rs.save_to_ply.option_ply_normals, True)
        ply.set_option(rs.save_to_ply.option_ignore_color, False)
        print("Saving mesh...")
        # Apply the processing block to the frameset which contains the depth frame and the texture
        ply.process(depth_frame)
        print("Done")
    
#export (r"C:\Users\pitsai\Documents\GitHub\intuitive-robotic-plastering\data\TEST.ply", mesh=False, pc=True)