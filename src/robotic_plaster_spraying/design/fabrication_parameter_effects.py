from compas.geometry import closest_point_in_cloud
from compas.geometry import distance_point_point
from compas.geometry import is_point_on_line
from robotic_plaster_spraying.utilities_fabrication.data_gathering import remapValues

def UserInputforEnhancingEffect(Pts, v_min, v_max, Ed_min, Ed_max):
    # Create distance dictionary
    distance_dict = {}

    for i in range(len(Pts)):

        # gererate ptcloud out of the rest of the branches
        r_Pts = []
        for j in range(len(Pts)):
            if j != i:
                r_Pts.extend(Pts[j])

        # Iterate through each target plane and calculate the closest distance
        for k in range(len(Pts[i])):
            distance, Pt, idx = closest_point_in_cloud(Pts[i][k], r_Pts)

            if not distance_dict.get(i):
                distance_dict[i] = []

            distance_dict[i].append(distance)

    velocity_list = []
    Ed_list = []

    for key in distance_dict:

        velocity = remapValues(distance_dict[key],v_min,v_max)
        Ed = remapValues(distance_dict[key],Ed_min,Ed_max)

        velocity_list.append(velocity)
        Ed_list.append(Ed)

    return velocity_list, Ed_list

def Custom_Acceleration_and_Ed(polylines, edit_polylines, v_min, v_max, Ed_min, Ed_max):
    velocity_values_list = []
    Ed_values_list = []

    for polyline, e_polyline in zip(polylines, edit_polylines):

        distance_list = []

        for pt, e_pt in zip(polyline, e_polyline):
            distance = distance_point_point(pt, e_pt)
            distance_list.append(distance)

        velocity = remapValues(distance_list, v_min, v_max)
        Ed = remapValues(distance_list, Ed_min, Ed_max)

        velocity_values_list.append(velocity)
        Ed_values_list.append(Ed)

    return velocity_values_list, Ed_values_list
