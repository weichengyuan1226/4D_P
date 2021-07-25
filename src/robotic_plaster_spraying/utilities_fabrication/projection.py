try:
    import Rhino.Geometry as rg
except ImportError:
    import platform
    if platform.python_implementation() == 'IronPython':
        raise

from compas.geometry import Point, Line, Box, Vector, Polygon, Plane
from compas.geometry import is_intersection_line_triangle
from compas.geometry import intersection_line_triangle
from compas.geometry import bounding_box
from compas.geometry import intersection_line_plane
from compas.datastructures import Mesh
from compas.datastructures import meshes_join_and_weld
from compas_ghpython.artists import MeshArtist
from compas_rhino.geometry import RhinoMesh

# Mesh method

def RhinoToCompasMesh(mesh):
    """ Convert Rhino geometry objects to COMPAS """
    return RhinoMesh.from_geometry(mesh).to_compas()

def RhinoMeshData(mesh):
    """ Get verticies, face ID and average face normal from Rhino mesh """
    verticies = [rg.Point3d(mesh.Vertices.Item[i]) for i in range(mesh.Vertices.Count)]

    f_normal_a = rg.Vector3f(0,0,0)

    fIDs = []
    for i in range(mesh.Faces.Count):
        f_normal = mesh.FaceNormals.Item[i]
        f_normal_a += f_normal
        f = mesh.Faces.Item[i]
        if f.IsTriangle:
            vIDs = [f.A,f.B,f.C]
        else:
            vIDs = [f.A,f.B,f.C,f.D]
        fIDs.append(vIDs)

    average_normal = rg.Vector3d(f_normal_a/mesh.Faces.Count)
    average_normal.Unitize()

    return verticies, fIDs, average_normal

def QuadsToTriangles(mesh):

    for fkey in list(mesh.faces()):
        attr = mesh.face_attributes(fkey)
        attr.custom_only = True
        vertices = mesh.face_vertices(fkey)
        if len(vertices) == 4:
            a, b, c, d = vertices
            t1, t2 = mesh.split_face(fkey, b, d)
            mesh.face_attributes(t1, attr.keys(), attr.values())
            mesh.face_attributes(t2, attr.keys(), attr.values())

    return mesh

def PointProjectOnMesh(pts, projected_mesh, vector, Compas_pt = False, allow_to_skip = False):

    if type(projected_mesh) is not type(rg.Mesh()):
        artist = MeshArtist(projected_mesh)
        projected_mesh = artist.draw()

    if Compas_pt:
        pts = [rg.Point3d(pt.x, pt.y, pt.z) for pt in pts]
        vector = rg.Vector3d(vector.x, vector.y, vector.z)

    p_pts = []

    for i,pt in enumerate(pts):
        pt.X += 0.1
        pt.Y += 0.1
        pt.Z += 0.1
        m_p1 = pt+vector*10000
        m_p2 = pt-vector*10000
        line = rg.Line(m_p1,m_p2)

        point,fID = rg.Intersect.Intersection.MeshLine(projected_mesh,line)

        if len(point) >= 1:
            point = point[0]
        elif len(point)==0:
            if allow_to_skip:
                continue
            else:
                point = line.ClosestPoint(p_pts[-1],True)

        if Compas_pt:
            p_pts.append(Point(point.X, point.Y, point.Z))
        else:
            p_pts.append(point)

    return p_pts

def CompasPointProjectOnMesh(pts, mesh, vector):

    scale = 100

    if mesh.is_quadmesh():
        QuadsToTriangles(mesh)

    f_Pts = [mesh.face_coordinates(fkey) for fkey in mesh.faces()]

    project_Pts = []

    for i,pt in enumerate(pts):

        line = Line(pt + vector*scale, pt  -vector*scale)
        count = 0

        for f_Pt in f_Pts:
            if is_intersection_line_triangle(line, f_Pt):
                p_pt = intersection_line_triangle(line, f_Pt)
                project_Pts.append(p_pt)

    return project_Pts

def CapMesh(mesh, reverse = False):

    b_box_pts = mesh.bounding_box()
    b_box = Box.from_bounding_box(b_box_pts)

    b_box_centroid = Point(0,0,0)
    for pt in b_box.vertices:
        b_box_centroid += pt
    b_box_centroid = Point(b_box_centroid.x/8, b_box_centroid.y/8, b_box_centroid.z/8)

    a_normal = Vector(0,0,0)
    for fkey in mesh.faces():
        a_normal += mesh.face_normal(fkey)
    face_len = len(list(mesh.faces()))
    a_normal = Vector(a_normal.x/face_len, a_normal.y/face_len, a_normal.z/face_len)
    if reverse:
        a_normal = a_normal * -1

    max_angle = 0
    max_key = 100
    for key,face in enumerate(b_box.faces):
        pts = []
        for v_key in face:
            pts.append(b_box.vertices[v_key])
        rec_centroid = Polygon(pts).centroid
        vec = Vector.from_start_end(rec_centroid, b_box_centroid)
        angle = vec.angle(a_normal)
        if angle > max_angle:
            max_angle = angle
            max_key = key

    pts = [b_box.vertices[v_key] for v_key in b_box.faces[max_key]]
    rec = Polygon(pts)
    plane = Plane(rec.centroid, rec.normal)

    cap_mesh = mesh.copy()

    for key in mesh.vertices():
        pt = Point(*mesh.vertex_coordinates(key))
        line = Line(pt+rec.normal*1000, pt-rec.normal*1000)
        int_pt = intersection_line_plane(line, plane)

        cap_mesh.vertex_attributes(key, ['x', 'y', 'z'], [int_pt[0], int_pt[1], int_pt[2]])

        if mesh.is_vertex_on_boundary(key):
            mesh.vertex_attributes(key, ['x', 'y', 'z'], [int_pt[0], int_pt[1], int_pt[2]])

    close_mesh = meshes_join_and_weld([mesh,cap_mesh])

    return close_mesh
