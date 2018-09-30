import json
import math


# Basic usage: initialize with MoveGPSData(5, .1) (for example), call import_paths_and_coors with the tuple and the gpx,
# then call move_points() and will print the number of points changed and will return the gpx data
class MoveGPSData:
    unique_paths = {}
    coordinate_list = []
    file = 'maryville_college_woods.geojson'
    gpx_list = []
    points_changed = 0

    num_points_considered = 5
    slope_threshold = .1
    distance_threshold = 10
    distance_degree_threshold = 0

    def __init__(self, pts_considered, sl_threshold, dist_threshold, gpx_raw):
        self.num_points_considered = pts_considered
        self.slope_threshold = sl_threshold
        self.distance_threshold = dist_threshold
        self.distance_degree_threshold = dist_threshold / 111320.0

        if gpx_raw is not None:
            self.gpx_list = gpx_raw
        else:
            self.gpx_list = [(35.7497170, -83.9599710), (35.7497350, -83.9599540), (35.7497680, -83.9599200),
                             (35.7498040, -83.9598760), (35.7498700, -83.9597750)]

    @staticmethod
    def get_projected_point_on_line_v1(v1, v2, p):
        # get dot product of e1, e2
        e1 = (v2[0] - v1[0], v2[1] - v1[1])
        e2 = (p[0] - v1[0], p[1] - v1[1])
        # dot product
        val_dp = e1[0] * e2[0] + e1[1] * e2[1]
        # get squared length of e1
        len2 = e1[0] * e1[0] + e1[1] * e1[1]
        point = ((v1[0] + (val_dp * e1[0]) / len2), (v1[1] + (val_dp * e1[1]) / len2))
        return point

    @staticmethod
    def get_projected_point_on_line_v2(v1, v2, p):
        m = (v2[1] - v1[1]) / (v2[0] - v1[0])
        b = v1[1] - (m * v1[0])

        x = (m * p[1] + p[0] - m * b) / (m * m + 1)
        y = (m * m * p[1] + m * p[0] + b) / (m * m + 1)

        return x, y

    def import_paths_and_coors(self, paths_nodes_tuple):
        self.unique_paths = paths_nodes_tuple[0]
        self.coordinate_list = paths_nodes_tuple[1]

    def import_geojson(self, file_name):
        f = open(file_name, 'r')
        data = json.load(f)
        f.close()

        for feature in data['features']:
            id_str = feature['properties']['@id']
            coors = feature['geometry']['coordinates']
            self.unique_paths[id_str] = coors

            for unique_coordinate_pair in coors:
                self.coordinate_list.append(unique_coordinate_pair.copy() + [id_str])

    def move_points(self, i):        
        if i == 0:
            gpx_slope = (self.gpx_list[1][1] - self.gpx_list[0][1]) / (self.gpx_list[1][0] - self.gpx_list[0][0])
        elif i == len(self.gpx_list) - 1:
            gpx_slope = (self.gpx_list[i][1] - self.gpx_list[i - 1][1]) / \
                        (self.gpx_list[i][0] - self.gpx_list[i - 1][0])
        else:
            if (self.gpx_list[i + 1][0] - self.gpx_list[i - 1][0]) != 0:
                gpx_slope = (self.gpx_list[i + 1][1] - self.gpx_list[i - 1][1]) / \
                            (self.gpx_list[i + 1][0] - self.gpx_list[i - 1][0])
            else:
                gpx_slope = -1

        # Find the points closest to the gpx point
        distance_id_dict = {}
        for coordinates in self.coordinate_list:
            dist = math.sqrt(pow((coordinates[0] - self.gpx_list[i][0]), 2) +
                                pow((coordinates[1] - self.gpx_list[i][1]), 2))
            distance_id_dict[dist] = (coordinates[0], coordinates[1], coordinates[2])
        distance_keys = sorted(list(distance_id_dict.keys()))
        # print str(distance_keys)

        # Look at the closest 5 points - for each OSM point
        osm_slope_list = []
        osm_slope_divisions = []
        for j in range(0, min(self.num_points_considered, len(distance_keys))):
            
            # Apply the distance threshold specified in the constructor
            # The distance was converted to degrees of lat/long so it can be applied
            # print distance_keys[j], self.distance_degree_threshold
            if distance_keys[j] <= self.distance_degree_threshold:
                way_id = distance_id_dict[distance_keys[j]]

                # Get the closet two OSM points on the same curve/section way
                curve_options = self.unique_paths[way_id[2]]
                osm_distance_dict = {}  # maps distance between index
                for curve_coordinate in curve_options:
                    inside_sqrt = pow(way_id[0] - curve_coordinate[0], 2) + pow(way_id[1] - curve_coordinate[1], 2)
                    dist_to_osm = math.sqrt(inside_sqrt)
                    osm_distance_dict[dist_to_osm] = (curve_coordinate[0], curve_coordinate[1], way_id[2])
                    # print(dist_to_osm)
                osm_distance_keys = sorted(list(osm_distance_dict.keys()))
                # The who keys we want are at index 1 and 2 since index 0 should be 0.0 or the point itself
                if len(osm_distance_keys) < 3:
                    break
                first_pt_tuple = osm_distance_dict[osm_distance_keys[1]]
                second_pt_tuple = osm_distance_dict[osm_distance_keys[2]]

                # Calculate slope between these two points
                osm_slope = (second_pt_tuple[1] - first_pt_tuple[1]) / (second_pt_tuple[0] - first_pt_tuple[0])
                osm_slope_list.append((osm_slope, first_pt_tuple, second_pt_tuple))

        # Now select the slope of the OSM data that is closest to our GPX curve slope

        smallest_slope_diff_div = 100000
        smallest_slope_diff_div_index = -1
        for j in range(0, len(osm_slope_list)):
            slope_div = abs(1 - abs(osm_slope_list[j][0] / gpx_slope))
            osm_slope_divisions.append(slope_div)

            # print slope_div, smallest_slope_diff_div
            # print slope_div, self.slope_threshold

            if slope_div < smallest_slope_diff_div and slope_div <= self.slope_threshold:  # threshold applied
                smallest_slope_diff_div = slope_div
                smallest_slope_diff_div_index = j

        if smallest_slope_diff_div_index != -1:
            # We are changing the point to on the path with this slope
            ind = smallest_slope_diff_div_index
            v1 = (osm_slope_list[ind][1][0], osm_slope_list[ind][1][1])
            v2 = (osm_slope_list[ind][2][0], osm_slope_list[ind][2][1])
            pnt = (self.gpx_list[i][0], self.gpx_list[i][1])
            proj2 = self.get_projected_point_on_line_v2(v1, v2, pnt)
            self.gpx_list[i] = proj2

            self.points_changed += 1

        # Else we are not changing the point at all

        return self.gpx_list[i], self.points_changed
                