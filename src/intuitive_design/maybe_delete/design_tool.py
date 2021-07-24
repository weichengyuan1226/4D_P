from __future__ import absolute_import

import rhinoscriptsyntax as rs

class Crvfilter():
    """This is a class to apply filters to points"""

    def __init__(self, crv_points):
        self.crv_points = []
        self.crv = None
    

    def rebuild_crv(self, curve, degree, lenght_list, rebuild_percentage):
        rebuild = lenght_list * float(rebuild_percentage/100.0)
        new_curve = rs.RebuildCurve(curve, degree= degree, point_count=rebuild)
        return new_curve

    
    def offset_crv(self, curve, direction, distance):
        curve = rs.OffsetCurve(c, direction, distance)
        curve.rebuild_crv()
        return curve
