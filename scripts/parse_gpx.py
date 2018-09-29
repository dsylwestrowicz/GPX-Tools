import xml.etree.ElementTree as ET
#  For now we have a hard coded prefix over here.
#  We might want to fix this later
prefix = '{http://www.topografix.com/GPX/1/1}'

class Activity:
    #   Initialize new activity taking the GPX file name as the argument
    def __init__(self, fileName):
        self.tree = ET.parse(fileName)
    
    #   Return all of the coordinates of the data points in the GPX file
    def getCoordinates(self):
        root = self.tree.getroot()
        coords = []
        for child in root:
            if child.tag == prefix+'trk':
                for grand_child in child:
                    if grand_child.tag == prefix+'trkseg':
                        for data_point in grand_child:
                            coordinates = data_point.attrib["lat"], data_point.attrib["lon"]
                            coords.append(coordinates)

        return coords