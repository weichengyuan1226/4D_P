import compas
from compas.geometry import Frame
from compas.geometry.xforms import Transformation
from compas_ghpython.geometry import xtransformed
import rhinoscriptsyntax as rs
import Rhino.Geometry as rg
import scriptcontext as sc

__all__ = [
    "Point"
]

class Point(object):
    """Description of Point Class

    """

    def __init__(self, origin_plane, geo = None):
        """The point class
        """
        self.plane = origin_plane #origin plane of the point
        self.frame = self.frame_from_plane()
        self.geo = geo #point geometry in WorldXY

    def set_plane(self, plane):
        self.plane = plane # plane of the point
        self.frame = self.frame_from_plane()

    def frame_from_plane(self):
        """ generates as frame from the input origin_plane """
        return Frame(self.plane.Origin, self.plane.XAxis, self.plane.YAxis)

    def get_pose_quaternion(self):
        """ returns the point origin pose with quaternions as list """
        return self.frame.point + self.frame.quaternion

