import requests
import json
import copy

OVERPASS_URL = 'http://overpass-api.de/api/interpreter'
SEARCH_RADIUS = 25.0    #in meters

class Overpass_Query:
    #   Constructor for creating a new query, it takes the lat, lon of a data point.
    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon
    #   getPaths actually calls the query and performs the operations required to get
    #   a dictionary of paths, keyed on the pathId with the value being a list of 
    #   coordinate lists that are included in that path as well as a nodes_lookup list
    #   which stores lists of coordinates with the matching pathId
    def getPaths(self):
        overpass_query = '[out:json];(way["highway"](around:'+str(SEARCH_RADIUS)+', '+str(self.lat)+', '+str(self.lon)+');>;);out;'
        response = requests.get(OVERPASS_URL, params={'data': overpass_query})
        data = response.json()
        nodes = {}
        paths = {}
        nodes_lookup = []
        for element in data['elements']:
            if element["type"] == "node":
                nodes[element["id"]] = [element["lat"], element["lon"]]
        nodes_copy = copy.deepcopy(nodes)
        for element in data['elements']:
            if element["type"] == "way":
                for nodeId in element["nodes"]:
                    if element["id"] not in paths:
                        paths[element["id"]] = []
                    paths[element["id"]].append(nodes[nodeId])
                    nodes_copy[nodeId].append(element["id"])
        for node in nodes_copy.values():
            nodes_lookup.append(node)
        return paths, nodes_lookup
