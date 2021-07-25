#import Rhino.Geometry as rg
import rhinoscriptsyntax as rs
import random as r 
import intuitive_design.utilities.util as u

__all__ = [
    "scanData"
]

class scanData():
    """From a recorded data set, first we want to process the data set minimally. 
    We store this in a class so that we always have access to the original recorded data set. """ 

    def __init__(self, planes, points = None, timestamp = None): 
        self.planes = planes
        self.points = points
        self.usablePointSet = points # default is using all the points
        self.timestamp = timestamp 
    
    # methods for storing geometry with class  ------------------------------------------
    # these methods can be extended to also use Compas 
    def addReferenceGeometry_Curve(self, refCurve):
        self.refCurve = refCurve

    def addReferenceGeometry_Plane(self,refPlane):
        self.refPlane = refPlane

    def addReferenceGeometry_Vector(self, refVector):
        self.refVector = refVector


    def storeAllPoints(self):
        self.points = [plane.Origin for plane in self.planes] 

    def storePointSelection (self, proportionStart, proportionEnd, save = True):
        """this should be a useable pointset so the start and end points might need to be filtered out""" 
        IndexStart = int(proportionStart * len(self.points))
        IndexEnd = int(proportionEnd*len(self.points))
        usablePointSet = self.points[IndexStart: IndexEnd]     #we slice the list with a new start and end position
        usablePointCurve = u.makeCurveFromPoints(usablePointSet)  #curve from new list using the utils
        if save:
            self.usablePointSet = usablePointSet
            self.usablePointCurve = usablePointCurve
        return usablePointSet, usablePointCurve

    def generateRandomSelection(self): 
        """generating a random start and endpoint to produce variation""" 
        rand1 = r.random()
        rand2 = r.random() 
        
        if rand2 < rand1:  #if the nr of rand2 is bigger swap them
            temp = rand2
            rand2 = rand1
            rand1 = temp
        #selectionPoints = self.storePointSelection(rand1, rand2) // CHECK IF I NEED TO DELETE THAT
        selectionPoints = u.getPointSelection (rand1, rand2, self.usablePointSet)
        return selectionPoints

    def generateRandomSelection_similarLength(self, domainlength = .3): 
        """generating a random start and endpoint within specific domains to produce variation"""
        rand1 = r.random() * ( 1-domainlength)
        rand2 = rand1 + domainlength

        #selectionPoints = self.storePointSelection(rand1, rand2) // CHECK IF I NEED TO DELETE THAT
        selectionPoints = u.getPointSelection (rand1, rand2, self.usablePointSet)
        return selectionPoints
        