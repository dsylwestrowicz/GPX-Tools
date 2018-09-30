import MoveGPSData
import parse_gpx
import generate_path_data
import copy

def main():
    fileName = 'activity.gpx'
    activity = parse_gpx.Activity(fileName)
    coordinates = activity.getCoordinates()
    new_coordinates = copy.deepcopy(coordinates)
    i = 0
    total_pts_changed = 0
    query = generate_path_data.Overpass_Query(coordinates[0][0], coordinates[0][1])
    paths, nodes = query.getPaths()

    for coordinate in coordinates:
        move = MoveGPSData.MoveGPSData(10, 1.6, 16, coordinates)
        a = paths, nodes
        move.import_paths_and_coors(a)
        new_coordinates[i], point_change = move.move_points(i)
        total_pts_changed += point_change
        i = i + 1
    activity.modifyCoordinates(new_coordinates)

    print "Pts changed: " + str(total_pts_changed)
    print "Total points: " + str(len(coordinates))

if __name__ == '__main__':
    main()