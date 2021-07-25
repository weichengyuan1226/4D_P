import Rhino.Geometry as rg
import rhinoscriptsyntax as rs
import copy as c
import intuitive_design.utilities.util as u

__all__ = [
    "filters_BaseClass",
    "filter_stretchAlongCurve",
    "filterpointsSet_OnCurve",
    "filter_offset"
]

class filters_BaseClass():
    """ this is a class for taking the initially recorded data points, transforming them to a new location and manipulating them """ 
    def __init__(self, filterpoints, plane = None):
        self.filterpoints = filterpoints #all points
        self.plane = plane
        self.planeTransformed = c.deepcopy(self.filterpoints.refPlane)
        #default is for the points to be here
        self.points = c.deepcopy(self.filterpoints.usablePointSet) #deep copy vs shallow copy: create a copy without modifying the original to create a fully independent clone of the original object and all of its children.
        #store transform points here
        self.pointsTransformed = c.deepcopy(self.points) 

    def generateNewPointSubset_Random(self):
        self.points = self.filterpoints.generateRandomSelection()

    def generateNewPointSubset_DomainLength(self, domainLength = .3):
        self.points = self.filterpoints.generateRandomSelection_similarLength()

    def transform_points_plane(self):
        # solve for transform
        self.transform = rg.Transform.PlaneToPlane(self.filterpoints.refPlane, self.plane) #here we use the reference plane defined in scan_data

        for point in self.pointsTransformed:
             point.Transform(self.transform)
        self.planeTransformed.Transform(self.transform)
        return self.pointsTransformed, self.planeTransformed

    def transform_points_planes(self):
        # solve for transform

        pass

    def scale (self, xscale, yscale, zscale):

        # scaling should happen before transforming because we will use the initial frame as the reference frame
        scaled_points= rs.ScaleObjects(self.pointsTransformed, self.filterpoints.refPlane.Origin, [xscale, yscale, zscale])  
        temp = rs.coerce3dpointlist(scaled_points)
        self.pointsTransformed = temp
        return self.pointsTransformed
        
    # def updatePlanesFromPoints(self):
    #     for point, plane in zip(self.points, self.planes):
    #         plane = rs.MovePlane(plane, point)
    # add more methods that would be used often ie non uniform scale

class filter_stretchAlongCurve(filters_BaseClass):
    """ this is a class for making custom filters. It should inherit the properties and methods of the filters Base class. If we want to make new filters, we should set them up in the same way""" 

    def __init__(self, filterpoints, plane, curve, refvector):
        filters_BaseClass.__init__(self, filterpoints, plane) 
        self.curve = curve
        self.refVector = refvector

       
    def generatenewpoints(self):
        numberpoints = len(self.points)
        curveparams = rg.Curve.DivideByCount(self.curve, numberpoints, True)
        self.planes = [] 
        
        self.pointsTransformed = c.deepcopy(self.points)
        
        for point, param in zip (self.pointsTransformed, curveparams):
            
            #make plane)
            tan = rg.Curve.TangentAt(self.curve, param)
            pointCurve = rg.Curve.PointAt(self.curve, param) 
            plane =  u.getPlaneFromCurveTangentRefVec(tan, self.refVector, pointCurve) 
            self.planes.append(plane)
            
            localtransform = rg.Transform.PlaneToPlane(self.filterpoints.refPlane, plane)
            point.Transform(localtransform )
            # transform 
        return self.pointsTransformed

class filter_offset(filters_BaseClass):
    """ this is a class for making custom filters. It should inherit the properties and methods of the filters Base class. If we want to make new filters, we should set them up in the same way""" 

    def __init__(self, filterpoints, points_transformed): #here wew extend the baseclass 
        filters_BaseClass.__init__(self, filterpoints, points_transformed) #, points_transformed
        self.points_transformed = points_transformed
       
    def offset_points(self, offset_vector, distance=None, degree=3, rebuild_percentage=10, save=False):
        if distance is None:
            distance = rs.VectorLength(offset_vector)
        elif distance == 0:
            raise ValueError("distance cannot be 0")

        #make a curve out of the filterpoints
        c = rs.AddCurve(self.points_transformed, degree=degree)
        u.rebuildCrv(c, degree=degree, rebuild_percentage=rebuild_percentage)
        offset_curve = rs.OffsetCurve(c, offset_vector, distance) #for some reason is a bit computationally heavy
        if offset_curve is None:
            raise Exception("Rhino was unable to offset the curve. Check the distance value, or pray to Freyja.")
        offset_curve_points = rs.DivideCurve(offset_curve, len(self.points_transformed)-1)

        # update the points in the filterpoints only when save if true
        if save:
            self.points_transformed = offset_curve_points
            #self.filterpoints.updatePlanesFromPoints(points_transformed)

        return offset_curve, offset_curve_points

    def generatenewpoints_CurveDomain(self, domain):

        numberpoints = len(self.points)
        rangeDomain = domain[1]-domain[0]
        increment =rangeDomain/numberpoints

        self.planes = [] 
        self.pointsTransformed = c.deepcopy(self.points)

        param = domain[0]

        for i in range(int(numberpoints)):

            point = self.pointsTransformed[i]
            tan = rg.Curve.TangentAt(self.curve, param)
            pointCurve = rg.Curve.PointAt(self.curve, param) 
            plane =  u.getPlaneFromCurveTangentRefVec(tan, self.refVector, pointCurve) 
            self.planes.append(plane)
            
            localtransform = rg.Transform.PlaneToPlane(self.filterpoints.refPlane, plane)
            point.Transform(localtransform )
            param = param + increment 

        return self.pointsTransformed

class filterpointsSet_OnCurve():

    """ this is a clsas that stores several filters together """

    def __init__(self, filter, curve, refVector): # i am using an input surface here 
        self.Filter = filter # initial list of data points 
        self.curve = curve
        self.refVector =  refVector

    def getPlanes(self, distance): 
        self.planes = u.getPlanesFromCurves(self.curve, distance, self.refVector)
    
    def getDomainSeries(self, noSegments, ratioPlanesSpace = .9, domainStart= 0, domainEnd = 1):
        
        # assumes curve domain
        self.domains = [] 
        totalDomain = 1.00 - domainStart
        
        DomainlengthSegment = totalDomain /noSegments 
        DomainlengthPlanes = DomainlengthSegment * ratioPlanesSpace
        domainStart = 0.00 
        
        for i in range(noSegments):
            domainEnd = domainStart + DomainlengthPlanes
            newDomain = [domainStart, domainEnd]
            self.domains.append(newDomain)
            
            domainStart = domainStart + DomainlengthSegment
    
    def applyBaseFilterwithRandomSelectionAlongCurve(self, domainlength):
        
        self.points = [] 
        self.filterList = [] 
        
        for plane in self.planes:
            # make a copy of our filter so we can change the points
            filter = c.deepcopy(self.Filter)
            filter.curve = self.curve
            self.filterList.append(filter) 
            
            # replace the filter plane with the new plane
            filter.plane = plane 
            
            filter.generateNewPointSubset_DomainLength(domainlength)
            #filter.generateNewPointSubset_Random()
            
            newPoints = filter.transformPoints()
            self.points.extend(newPoints)

    def applyStretchedFilterAlongCurve(self, noIterations):
        
        self.points = [] 
        self.filterList = [] 
        self.planes = [] 
        
        for i in range(noIterations):
            filter = c.deepcopy(self.Filter)
            filter.curve = self.curve
            self.filterList.append(filter) 
        
            domain = self.domains[i] 
            filter.generatenewpoints_CurveDomain(domain) 
            self.points.extend(filter.pointsTransformed)
            self.planes.extend(filter.planes)

#Derived class filterclass inherits features from the base class where new features can be added to it. This results in re-usability of code.
