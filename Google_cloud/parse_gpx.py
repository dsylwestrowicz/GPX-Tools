import xml.etree.ElementTree as ET
#  For now we have a hard coded prefix over here.
#  We might want to fix this later
prefix = '{http://www.topografix.com/GPX/1/1}'

class Activity:
    #   Initialize new activity taking the GPX file name as the argument
    def __init__(self, fileName):
        self.fileName = fileName
        self.tree = ET.parse(fileName)
        ET.register_namespace('',"http://www.topografix.com/GPX/1/1")
    
    #   Return all of the coordinates of the data points in the GPX file
    def getCoordinates(self):
        root = self.tree.getroot()
        coords = []
        for child in root:
            if child.tag == prefix+'trk':
                for grand_child in child:
                    if grand_child.tag == prefix+'trkseg':
                        for data_point in grand_child:
                            coordinates = float(data_point.attrib["lat"]), float(data_point.attrib["lon"])
                            coords.append(coordinates)

        return coords
    
    #   Takes a list of coordinate tuples (must list all in the same order as returned
    #   by getCoordinates). This will write a new GPX file and return the name of the
    #   newly created file
    def modifyCoordinates(self, coords, newFile):
        root = self.tree.getroot()
        i = 0

        for child in root:
            if child.tag == prefix+'trk':
                for grand_child in child:
                    if grand_child.tag == prefix+'trkseg':
                        for data_point in grand_child:
                            data_point.attrib["lat"] = str(coords[i][0])
                            data_point.attrib["lon"] = str(coords[i][1])
                            i = i + 1
        self.tree.write(newFile)
