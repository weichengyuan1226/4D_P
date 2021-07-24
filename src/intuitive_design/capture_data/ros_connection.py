from __future__ import absolute_import

import rhinoscriptsyntax as rs
import compas.geometry as cg
import os
import json
import itertools
from datetime import datetime
from scriptcontext import sticky
from compas_ghpython.utilities import update_component
from compas.geometry import Frame
from compas.geometry import Transformation

__all__ = [
    "Sensordata"
]

class Sensordata():
    """receives HTC Vive poses from controller and lighthouses and transforms their position into the world coordinate system.
    ROS - master and receiving notes are set outside this class
    """

    scale= 1000

    def __init__(self, buttons):
        self.buttons = None
        self.pose = None
        

    #receiving data from ROS

    """receive controller buttons from ROS

    returns controller name, axis and buttons
    """

    def contr_buttons(self):
        controller_buttons = sticky['controller_buttons']
        controller_name = controller_buttons['header']['frame_id']
        axes = controller_buttons['axes']
        self.buttons = controller_buttons['buttons']
        axes_trackpadX, axes_trackpadY, trigger = axes
        menu_button, trigger, trackpad_pressed, side_button = self.buttons
        return controller_name, axes, self.buttons

    """receive pose and posestamped from ROS 

    returns a Frame
    """

    def pose_calc_tf(self):
        controller_pose = sticky['controller_pose']
        translation = controller_pose['transforms'][0]['transforms']['translation']
        rotation = controller_pose['transforms'][0]['transform']['rotation']
        centerpoint =[translation['x'], translation['y'], translation['z']]
        quaternion = [rotation['x'], rotation['y'], rotation['z'], rotation['w']]
        self.pose = Frame.from_quaternion(quaternion, centerpoint)
        return self.pose

    def pose_calc_posestamped(self, sticky_name):
        translation = sticky_name['pose']['position']
        rotation = sticky_name['pose']['orientation']
        centerpoint =[translation['x'], translation['y'], translation['z']]
        quaternion = [rotation['w'], rotation['x'], rotation['y'], rotation['z']]
        self.pose = Frame.from_quaternion(quaternion, centerpoint)
        return self.pose

    #transforming frame-data from ROS
    """transforms the pose from ROS to global coordinate system for Rhino

    returns Plane and Plane delete
    """
    
    @staticmethod                     
    def from_world_to_world_vive():
        #world
        world_point = [0.0, 0.0, 0.0]
        orient = {'x': 0.0, 'y': 0.0, 'z': 0.0, 'w': -1.0}
        quaternion = [orient['w'], orient['x'], orient['y'], orient['z']]
        WCF= Frame.from_quaternion(quaternion, world_point) 

        #world_vive
        world_vive_point= [0.0, 0.0, 2.265]
        world_vive_orient= {'x': 0.707106781187, 'y': 0.0, 'z': 0.0, 'w': 0.707106781187}
        world_vive_quaternion = [world_vive_orient['w'], world_vive_orient['x'], world_vive_orient['y'], world_vive_orient['z']]
        RCF= Frame.from_quaternion(world_vive_quaternion, world_vive_point)
        t_RCF= cg.Frame.from_transformation(cg.Transformation.from_frame(WCF) * cg.Transformation.from_frame(RCF))
        RCF_plane = rs.PlaneFromFrame(t_RCF[0], t_RCF[1], t_RCF[2])
        return t_RCF

    def transform_pose_list(self, controller_frame):
        t_RCF = Sensordata.from_world_to_world_vive()
        t_frame= cg.Frame.from_transformation(cg.Transformation.from_frame(t_RCF) * cg.Transformation.from_frame(controller_frame))
        t_plane = rs.PlaneFromFrame(t_frame[0], t_frame[1],t_frame[2])
        origin= [t_frame[0].x, t_frame[0].y, t_frame[0].z]
        return t_plane, origin

    #save data

    def save_to_json(self, name_dict, DATA):
        reg = json.dumps(name_dict, sort_keys = True, indent=3, separators=(',', ': '))
        now = datetime.now() # current date and time
        date_time = now.strftime("%Y_%m_%d_%H_%M_%S")

        filename = "intuitive_plastering{}.json".format(date_time)
        PATH = os.path.join(DATA, filename)
        with open(PATH, 'w') as outfile:
            outfile.write(reg)
