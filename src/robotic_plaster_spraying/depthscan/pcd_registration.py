import open3d as o3d
import numpy as np
import copy
import sys, os


def scan_transform(path):
    # f0 = Frame([-387.301909, -133.257742, 283.325066],[-0.336824,0.059392,0.939693],[-0.010316,-0.998181,0.059391])
    # f1 = Frame([-340.849729, -141.448641, 375.08018], [0.085832,-0.015135,0.996195], [-0.000653,-0.999885,-0.015134])
    # f2 = Frame([-331.10814, -79.970145, 375.1748618], [0.085832,-0.015135,0.996195], [-0.308498,-0.951148,0.01213])
    # f3 = Frame([-372.813453, -72.616259, 298.95883], [-0.27145,0.047865,0.961262], [-0.30371,-0.951992,-0.038361])
    # frames = [f0, f1, f2, f3]

    t0 = [[-0.336824, -0.010316, 0.941511, -387.301909],
          [0.05939,  -0.998181, 0.010311, -133.257742],
          [0.939693, 0.059391, 0.336824, 283.325066],
          [0.0000, 0.0000, 0.0000, 1.0000]]
    t1 = [[0.085832, -0.000653, 0.996309, -340.849729],
          [-0.015135, -0.999885, 0.000648, -141.448641],
          [ 0.996195, -0.015134, -0.085832, 375.08018],
          [ 0.0000, 0.0000, 0.0000, 1.0000]]
    t2 = [[0.085832, -0.308498, 0.947345, -331.10814],
          [-0.015135, -0.951148, -0.308365, -79.970145],
          [0.996195, 0.01213, -0.086308, 375.1748618],
          [0.0000, 0.0000, 0.0000, 1.0000]]
    t3 = [[-0.27145, -0.30371, 0.913277, -372.813453],
          [0.047865, -0.951992, -0.302358, -72.616259],
          [0.961262, -0.038361,  0.272955, 298.95883],
          [0.0000, 0.0000, 0.0000, 1.0000]]
    T = [t0, t1, t2, t3]
    pcd_list = []
    for i in range(len(T)):
        pcd = o3d.io.read_point_cloud(os.path.join(path, "auto_pc_%d.ply" % i))
        pcd.scale(1000, center = (0,0,0))
        # target_frame = Frame([-456.994, 285.767, 846.427], [-1.000, 0.004, -0.001], [-0.004, -1.000, -0.000])
        # target_frame = frames[i]
        # T = matrix_from_frame(target_frame)
        pcd_t = copy.deepcopy(pcd).transform(T[i])
        # o3d.visualization.draw_geometries([pcd, pcd_t])
        pcd_list.append(pcd_t)

    for i in range(len(pcd_list)):
        if i == 0:
            pcd_all = pcd_list[i]
        else:
            pcd_all += pcd_list[i]

    radius = 20
    print("Downsample with a voxel size 20")
    pcd_all_down = pcd_all.voxel_down_sample(20)

    #print("3-2. Estimate normal.")
    #pcd_all_down.estimate_normals(
    #    o3d.geometry.KDTreeSearchParamHybrid(radius=radius * 2, max_nn=30))

    # o3d.geometry.crop_point_cloud([pcd_all_down], (0,200,0),(200,200,400))
    o3d.visualization.draw_geometries([pcd_all_down])
    o3d.io.write_point_cloud(os.path.join(path, "final.ply"), pcd_all_down, write_ascii=True, compressed=False, print_progress=False)
    return "Done"

# scan_transform(r"D:\Git\intuitive-robotic-plastering\data\ply")

# def ICP_registration_pos(path):

#     def draw_registration_result(source, target, transformation):
#         source_temp = copy.deepcopy(source)
#         target_temp = copy.deepcopy(target)
#         source_temp.paint_uniform_color([1, 0.706, 0])
#         target_temp.paint_uniform_color([0, 0.651, 0.929])
#         source_temp.transform(transformation)
#         o3d.visualization.draw_geometries([source_temp, target_temp],
#                                         zoom=0.4459,
#                                         front=[0.9288, -0.2951, -0.2242],
#                                         lookat=[1.6784, 2.0612, 1.4451],
#                                         up=[-0.3402, -0.9189, -0.1996])

#     def display_inlier_outlier(cloud, ind):
#         inlier_cloud = cloud.select_by_index(ind)
#         outlier_cloud = cloud.select_by_index(ind, invert=True)

#         print("Showing outliers (red) and inliers (gray): ")
#         outlier_cloud.paint_uniform_color([1, 0, 0])
#         inlier_cloud.paint_uniform_color([0.8, 0.8, 0.8])
#         o3d.visualization.draw_geometries([inlier_cloud, outlier_cloud],
#                                         zoom=0.3412,
#                                         front=[0.4257, -0.2125, -0.8795],
#                                         lookat=[2.6172, 2.0475, 1.532],
#                                         up=[-0.0694, -0.9768, 0.2024])

#     t0 = [[-0.336824, -0.010316, 0.941511, -387.301909],
#           [0.05939,  -0.998181, 0.010311, -133.257742],
#           [0.939693, 0.059391, 0.336824, 283.325066],
#           [0.0000, 0.0000, 0.0000, 1.0000]]
#     t1 = [[0.085832, -0.000653, 0.996309, -340.849729],
#           [-0.015135, -0.999885, 0.000648, -141.448641],
#           [ 0.996195, -0.015134, -0.085832, 375.08018],
#           [ 0.0000, 0.0000, 0.0000, 1.0000]]
#     t2 = [[0.085832, -0.308498, 0.947345, -331.10814],
#           [-0.015135, -0.951148, -0.308365, -79.970145],
#           [0.996195, 0.01213, -0.086308, 375.1748618],
#           [0.0000, 0.0000, 0.0000, 1.0000]]
#     t3 = [[-0.27145, -0.30371, 0.913277, -372.813453],
#           [0.047865, -0.951992, -0.302358, -72.616259],
#           [0.961262, -0.038361,  0.272955, 298.95883],
#           [0.0000, 0.0000, 0.0000, 1.0000]]

#     T_list = [t0, t1, t2, t3]

#     threshold = 5
#     voxel_size = 18

#     for i in range(len(T_list)):
#         if i == 0:
#             pcd = o3d.io.read_point_cloud(os.path.join(path, "auto_pc_%d.ply" % i))
#             pcd.scale(1000, center = (0,0,0))
#             target = copy.deepcopy(pcd).transform(T_list[i])
#         else:
#             pcd = o3d.io.read_point_cloud(os.path.join(path, "auto_pc_%d.ply" % i))
#             pcd.scale(1000, center = (0,0,0))
#             source = copy.deepcopy(pcd)

#             reg_p2p = o3d.pipelines.registration.registration_icp(source, target, threshold, T_list[i],
#                                                           o3d.pipelines.registration.TransformationEstimationPointToPoint(),
#                                                           o3d.pipelines.registration.ICPConvergenceCriteria(max_iteration=2000))

#             source_temp = copy.deepcopy(source)
#             source_temp.transform(reg_p2p.transformation)
#             pcd_combined = target + source_temp
#             target = pcd_combined.voxel_down_sample(voxel_size=voxel_size)

#     # o3d.visualization.draw_geometries([target])
#     o3d.io.write_point_cloud(os.path.join(path, "ICP_final.ply"), target, write_ascii=True, compressed=False, print_progress=False)

def ICP_registration(path, transformation_list, build_mesh = False):

    def draw_registration_result(source, target, transformation):
        source_temp = copy.deepcopy(source)
        target_temp = copy.deepcopy(target)
        source_temp.paint_uniform_color([1, 0.706, 0])
        target_temp.paint_uniform_color([0, 0.651, 0.929])
        source_temp.transform(transformation)
        o3d.visualization.draw_geometries([source_temp, target_temp],
                                        zoom=0.4459,
                                        front=[0.9288, -0.2951, -0.2242],
                                        lookat=[1.6784, 2.0612, 1.4451],
                                        up=[-0.3402, -0.9189, -0.1996])

    def display_inlier_outlier(cloud, ind):
        inlier_cloud = cloud.select_by_index(ind)
        outlier_cloud = cloud.select_by_index(ind, invert=True)

        print("Showing outliers (red) and inliers (gray): ")
        outlier_cloud.paint_uniform_color([1, 0, 0])
        inlier_cloud.paint_uniform_color([0.8, 0.8, 0.8])
        o3d.visualization.draw_geometries([inlier_cloud, outlier_cloud],
                                        zoom=0.3412,
                                        front=[0.4257, -0.2125, -0.8795],
                                        lookat=[2.6172, 2.0475, 1.532],
                                        up=[-0.0694, -0.9768, 0.2024])

    threshold = 12
    # voxel_size = 23
    voxel_size = 15

    for i in range(len(transformation_list)):
        if i == 0:
            pcd = o3d.io.read_point_cloud(os.path.join(path, "auto_pc_%d.ply" % i))
            pcd.scale(1000, center = (0,0,0))
            target = copy.deepcopy(pcd).transform(transformation_list[i])
        else:
            pcd = o3d.io.read_point_cloud(os.path.join(path, "auto_pc_%d.ply" % i))
            pcd.scale(1000, center = (0,0,0))
            source = copy.deepcopy(pcd)

            reg_p2p = o3d.pipelines.registration.registration_icp(source, target, threshold, transformation_list[i],
                                                          o3d.pipelines.registration.TransformationEstimationPointToPoint(),
                                                          o3d.pipelines.registration.ICPConvergenceCriteria(max_iteration=2000))

            source_temp = copy.deepcopy(source)
            source_temp.transform(reg_p2p.transformation)
            pcd_combined = target + source_temp
            target = pcd_combined.voxel_down_sample(voxel_size=voxel_size)

    if build_mesh:
        target.estimate_normals()
        # radii = [10, 20, 40, 80]
        # rec_mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(target, o3d.utility.DoubleVector(radii))

        mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(target, depth=12)

        densities = np.asarray(densities)
        vertices_to_remove = densities < np.quantile(densities, 0.08)
        mesh.remove_vertices_by_mask(vertices_to_remove)

        # o3d.visualization.draw_geometries([mesh])
        o3d.io.write_triangle_mesh(os.path.join(path, "ICP_final_mesh.obj"), mesh)
    else:
        o3d.io.write_point_cloud(os.path.join(path, "ICP_final.ply"), target, write_ascii=True, compressed=False, print_progress=False)

# ICP_registration(r"D:\Git\intuitive-robotic-plastering\data\ply")

def auto_registration(path):
    def draw_registration_result_original_color(source, target, transformation):
        pcd=[]

        source_temp = copy.deepcopy(source)
        source_temp.transform(transformation)
        pcd = source_temp + target
        new_pcd = o3d.geometry.PointCloud.voxel_down_sample(pcd,0.01)

        new_pcd.normals = o3d.utility.Vector3dVector(np.zeros((1, 3)))  # invalidate existing normals
        new_pcd.estimate_normals()

        distances = new_pcd.compute_nearest_neighbor_distance()
        avg_dist = np.mean(distances)
        radius =  4*avg_dist

        # pc_np = np.asarray(new_pcd.points)
        # f_ID =  delaunay_from_points_numpy(pc_np)
        # mesh = Mesh.from_vertices_and_faces(pc_np, f_ID)
        # mesh.to_obj(r"C:\\Users\\yoyot\\Documents\\GIT\\intuitive-robotic-plastering\\data\\ply\\final_mesh.obj")

        # o3d.visualization.draw_geometries([new_pcd],
        #                         zoom=0.5,
        #                         front=[-0.2458, -0.8088, 0.5342],
        #                         lookat=[1.7745, 2.2305, 0.9787],
        #                         up=[0.3109, -0.5878, -0.7468])
        # print(mesh)
        return new_pcd

    # print("1. Load two point clouds and show initial pose")
    for i in range(1):
        if i == 0:
            source = o3d.io.read_point_cloud(os.path.join(path, 'auto_pc_0.ply'))
            target = o3d.io.read_point_cloud(os.path.join(path, 'auto_pc_1.ply'))
        else:
            source = new_pcd
            target = o3d.io.read_point_cloud(os.path.join(path, 'auto_pc_%s.ply' % str(i+1)))

        # colored pointcloud registration
        # This is implementation of following paper
        # J. Park, Q.-Y. Zhou, V. Koltun,
        # Colored Point Cloud Registration Revisited, ICCV 2017
        voxel_radius = [0.04, 0.02, 0.01]
        max_iter = [50, 30, 14]
        current_transformation = np.identity(4)
        print("3. Colored point cloud registration")
        for scale in range(3):
            iter = max_iter[scale]
            radius = voxel_radius[scale]
            print([iter, radius, scale])

            print("3-1. Downsample with a voxel size %.2f" % radius)
            source_down = source.voxel_down_sample(radius)
            target_down = target.voxel_down_sample(radius)

            print("3-2. Estimate normal.")
            source_down.estimate_normals(
                o3d.geometry.KDTreeSearchParamHybrid(radius=radius * 2, max_nn=30))
            target_down.estimate_normals(
                o3d.geometry.KDTreeSearchParamHybrid(radius=radius * 2, max_nn=30))

            print("3-3. Applying colored point cloud registration")
            result_icp = o3d.pipelines.registration.registration_colored_icp(
                source_down, target_down, radius, current_transformation,
                o3d.pipelines.registration.TransformationEstimationForColoredICP(),
                o3d.pipelines.registration.ICPConvergenceCriteria(relative_fitness=1e-6,
                                                                relative_rmse=1e-6,
                                                                max_iteration=iter))
            current_transformation = result_icp.transformation
            print(result_icp.transformation)


        pcd_all = source + target
        o3d.io.write_point_cloud(os.path.join(path, 'final.ply'),
                                pcd_all,
                                write_ascii=False,
                                compressed=False,
                                print_progress=False)

        new_pcd = draw_registration_result_original_color(source, target,
                                                result_icp.transformation)
    o3d.visualization.draw_geometries([new_pcd],
                            zoom=0.5,
                            front=[-0.2458, -0.8088, 0.5342],
                            lookat=[1.7745, 2.2305, 0.9787],
                            up=[0.3109, -0.5878, -0.7468])

    pc_np = np.asarray(new_pcd.points)
    f_ID =  delaunay_from_points_numpy(pc_np)
    mesh = Mesh.from_vertices_and_faces(pc_np, f_ID)
    mesh.to_obj(r"C:\\Users\\yoyot\\Documents\\GIT\\intuitive-robotic-plastering\\data\\ply\\final_mesh.obj")

# auto_registration(r"C:\\Users\\yoyot\\Documents\\GIT\\intuitive-robotic-plastering\\data\\ply")
