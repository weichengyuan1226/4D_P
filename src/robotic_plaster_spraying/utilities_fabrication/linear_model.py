try:
    import Rhino.Geometry as rg
except ImportError:
    import platform
    if platform.python_implementation() == 'IronPython':
        raise

from compas.datastructures import Mesh
from compas.geometry import Point
from compas.geometry import Polyline
from compas.geometry import Translation
from compas.geometry import Vector
from compas.geometry import Line
import math


def remapValue(v,ori_Min,ori_Max,targetMin,targetMax):
    rv = ((v-ori_Min)/(ori_Max-ori_Min))*(targetMax-targetMin)+targetMin
    return rv


def scale(val, src, dst):
    #Scale (map) the given value from the scale of src to the scale of dst.
    return ((val - src[0]) / (src[1]-src[0])) * (dst[1]-dst[0]) + dst[0]


def projectPtstoMesh(points,normal,mesh):

    p_points = rg.Intersect.Intersection.ProjectPointsToMeshes([mesh], points, normal,0.0)
    p_curve = Polyline(p_points)

    c_parameters = []
    for i in range(len(points)-1):
        c_parameters.append(scale(i, (0.0, len(points)-1), (0.0, 1.0)))
    p_points = []
    for i in c_parameters:
        p_points.append(p_curve.point(i,True))
    return p_points


def visualize(base_mesh, velocity, Ed, layer_number, projected_points, ave_normals, plastering=True, grinding=False, m_scale=False, mm_scale=True):
    # Tree to list
    velocity_tree = [list(b) for b in velocity.Branches]
    Ed_tree = [list(b) for b in Ed.Branches]
    projected_points_tree = [list(b) for b in projected_points.Branches]

    if len(layer_number)==1:
        layer_number = [layer_number[0] for i in range(len(projected_points_tree))]

    ### Setup ###
    simulate_Mesh = Mesh()
    Max_velocity = 1.0

    # Thickness
    mesh_Pts_T = {}
    layer_index = {}

    # Mesh Pts
    mesh_Pts = []
    for i in range(base_mesh.Vertices.Count):
        pt = Point(float(base_mesh.Vertices.Item[i].X),float(base_mesh.Vertices.Item[i].Y),float(base_mesh.Vertices.Item[i].Z))
        mesh_Pts.append(pt)

    #translate projected_points into compas
    projected_points_tree_compas = []
    for pts in projected_points_tree:
        projected_points = []
        for pt in pts:
            p = Point(pt[0], pt[1], pt[2])
            projected_points.append(p)
        projected_points_tree_compas.append(projected_points)

    ### Calculate thickness ###
    for i,p_Pts in enumerate(projected_points_tree_compas):
        velocity = velocity_tree[i]
        ed_to_the_transformed_mesh = Ed_tree[i]

        for j,pt in enumerate(p_Pts):
            # Generate velocity, radius and thickness
            theta = remapValue( velocity[j], 0.1,1.0, 0,180 )
            value = math.cos(math.radians(theta))
            v = remapValue( value, -1.0,1.0, 0.1,Max_velocity )

            if plastering == True:
                radius = ed_to_the_transformed_mesh[j]/2
                if m_scale == True:
                    #Layer_thickness = remapValue(ed_to_the_transformed_mesh[j],0.3,0.5,0.004,0.002)

                    if ed_to_the_transformed_mesh[j] < 0.3:
                        Layer_thickness = remapValue(ed_to_the_transformed_mesh[j],0.2,0.5,0.003,0.006)
                    else:
                        Layer_thickness = remapValue(ed_to_the_transformed_mesh[j],0.3,0.5,0.006,0.003)
                if mm_scale == True:
                    #Layer_thickness = remapValue(ed_to_the_transformed_mesh[j],300,500,4,2)

                    if ed_to_the_transformed_mesh[j] < 300:
                        Layer_thickness = remapValue(ed_to_the_transformed_mesh[j],200,500,3,6)
                    else:
                        Layer_thickness = remapValue(ed_to_the_transformed_mesh[j],300,500,6,3)

            if grinding == True:
                if m_scale == True:
                    radius = 0.125/2
                    Layer_thickness = remapValue(velocity[j],0.04,0.05,0.002,0.001)
                if mm_scale==True:
                    radius = 125/2
                    Layer_thickness = remapValue(velocity[j],40,50,2,1)

            for k,m_Pt in enumerate(mesh_Pts):
                vertical_distance_to_spray_path = m_Pt.distance_to_point(pt)

                # Find Mesh Pts in spraying area
                if vertical_distance_to_spray_path < radius:
                    if not mesh_Pts_T.get(k):
                        mesh_Pts_T[k] = {'thickness_list':[],
                                            'Ed_list' : [] }

                    if ed_to_the_transformed_mesh[j] < 300:
                        remap_thickness = remapValue(vertical_distance_to_spray_path,0,radius,0,Layer_thickness*v*layer_number[i])
                    else:
                        remap_thickness = remapValue(vertical_distance_to_spray_path,0,radius,Layer_thickness*v*layer_number[i],0)

                    # First layer
                    if i == 0:
                        thickness = remap_thickness

                    # Check if vertex already has thickness from previous layer
                    else:
                        # if there is, add previous thickness with new thickness
                        if k in layer_index[i-1]:
                            thickness = remap_thickness + mesh_Pts_T[k]['thickness_list'][0]
                        else:
                            thickness = remap_thickness

                    mesh_Pts_T[k]['thickness_list'].append(thickness)
                    mesh_Pts_T[k]['Ed_list'].append(ed_to_the_transformed_mesh[j])


        vertices_num = mesh_Pts_T.keys()
        vertices_num.sort()

        #original
        for index in vertices_num:
            mesh_Pts_T[index]['thickness_list'] = [max(mesh_Pts_T[index]['thickness_list'])]
            if not layer_index.get(i):
                layer_index[i] = []
            layer_index[i].append(index)


    # Move Pts on Mesh
    thickness_list = []
    for i,Pt in enumerate(mesh_Pts):
        if not mesh_Pts_T.get(i):
            thickness = 0
        else:
            thickness = mesh_Pts_T[i]['thickness_list'][0]

        thickness_list.append(thickness)


        if plastering == True:
            thickness = ave_normals[i]*thickness
        if grinding == True:
            thickness = ave_normals[i]*-thickness

        x = Translation.from_vector(Vector(thickness[0],thickness[1],thickness[2]))

        Pt.transform(x)

        simulate_Mesh.add_vertex(x=Pt[0], y=Pt[1], z=Pt[2])


    # Generate new Mesh
    for i in range(base_mesh.Faces.Count):
        f = base_mesh.Faces.Item[i]
        if f.IsTriangle:
            vIDs = [f.A,f.B,f.C]
        else:
            vIDs = [f.A,f.B,f.C,f.D]
        simulate_Mesh.add_face(vIDs)

    return simulate_Mesh, thickness_list
