import Rhino.Geometry as rg
import rhinoscriptsyntax as rs 

__all__ = [
    "getPlanesFromCurves",
    "translatepointnewcoordinatesystem",
    "componentofbindira",
    "getPointSelection",
    "makeCurveFromPoints",
    "applyPlanes",
    "getPlaneFromCurveTangentRefVec",
    "rebuildCrv"
]

def translatepointnewcoordinatesystem(point, plane ): 
    """ this function translates a point in the world coodinate system to its coordinates in a 
     second coordinate system whose axes are given in coordinatesystem2 and whose origin is passed in separately 
    
    """ 
    vector = rg.Point3d.Subtract(point, plane.Origin) 
    

    xcomp = componentofbindira(plane.XAxis, vector)
    ycomp = componentofbindira(plane.YAxis, vector) 
    zcomp = componentofbindira(plane.ZAxis, vector) 
    
    newPoint = rg.Point3d(xcomp, ycomp, zcomp) 
    
    return newPoint 

def componentofbindira(vectora,vectorb, boolvisualize = False):
    """ this function solves for the length of vector b in the direction of a """  
    
   
    magb = rs.VectorLength(vectorb)
    unita = rs.VectorUnitize(vectora)
        
    origin = (0,0,0)
     #can't store false so save booleans as zero
    dotproduct = rs.VectorDotProduct(unita,vectorb)
    component = dotproduct 
    vectorindir = rs.VectorScale(unita,component)

        
    return component 

def getPointSelection(proportionStart, proportionEnd, listPoints):
    IndexStart = int(proportionStart * len(listPoints))
    IndexEnd = int(proportionEnd*len(listPoints))
    selectedPointSet = listPoints[IndexStart: IndexEnd]
    return selectedPointSet 

def makeCurveFromPoints(points):
    try:
        newCurve = rg.NurbsCurve.CreateInterpolatedCurve(points, 3)
        return newCurve
    except:
        print ("error making interpolated curve")
    return newCurve

def getPlanesFromCurves(curve,distance, refVector): 
    
    planes = [] 
    params = rg.Curve.DivideByLength(curve, distance, False)
    
    for param in params: 
        tan = rg.Curve.TangentAt(curve, param)
        point = rg.Curve.PointAt(curve, param) 
        plane =  getPlaneFromCurveTangentRefVec(tan, refVector, point) 
        planes.append(plane)
    return planes

def getPlaneFromCurveTangentRefVec(tangent, refZVector, point):
    newVec = rg.Vector3d.CrossProduct(tangent, refZVector)
    newPlane = rg.Plane(point, tangent, newVec)
    newPlane = rg.Plane(point, newVec, tangent)
    return newPlane
    
def applyPlanes(filterpoints, planes):
    #technically this should be a nested list 
    
    transformedPoints = []
    
    for newPlane in planes:
        transform = rg.Transform.PlaneToPlane(filterpoints.refPlane, newPlane)
        transform = rg.Transform.PlaneToPlane( newPlane, filterpoints.refPlane)
        #transformedPoints = [] 
        for point in filterpoints.points :
        
            point.Transform(transform)
            transformedPoints.append(point) 
            
    return transformedPoints

def rebuildCrv(curve, degree, rebuild_percentage):
    rebuild = len(rs.CurvePoints(curve)) * (rebuild_percentage/100.0)
    new_curve = rs.RebuildCurve(curve, degree= degree, point_count=rebuild)
    return new_curve