from csv import reader
from array import array
from shapely.geometry import Polygon
from shapely.geometry import Point
from shapely.ops import cascaded_union
import locale
import re
import sys
import getopt

coordinates_mcu = {}
coordinates_mem = {}
connect = {}
decimal_point = locale.localeconv()['decimal_point']
route_table = []
jumps_list = []
solution = ''
jumps_count = 0
current_line = 0

def serve_route_table(newpoly):
    global route_table
    first_route = None
    first_poly = None
    #Serving new poly to route table, concatenating routes according to polys interlaces
    for route in route_table:
        for poly in route:
            if (poly["layer"] == newpoly["layer"] and poly["poly"].intersects(newpoly["poly"])):
                poly["poly"] = cascaded_union( [poly["poly"], newpoly["poly"]] )
                if first_route == None:
                    first_route = route
                    first_poly = poly
                else:
                    first_poly["poly"] = cascaded_union( [first_poly["poly"], poly["poly"]] )
                    route.remove( poly )
                    first_route += route
                    route_table.remove( route )

    if first_route == None:
        route_table.append( [ newpoly, ] )

def serve_route_table_jump():
    global jumps_list
    first_route = None

    for jump in jumps_list:
        for route in route_table:
            for poly in route:
                if (poly["poly"].contains( jump )):
                    if first_route == None:
                        first_route = route
                    else:
                        first_route += route
                        route_table.remove( route )


def parse_poly(command, solution):

    global current_line

    poly_object = {}

    try:
        #Get number of points and layer
        edges_count = re.findall( "(?<=POLY)[^,]+(?=,)", command )
        if len(edges_count) != 1:
            print "Syntax error while getting points count in POLY, line #%d" % current_line
            exit()

        layer_number = re.findall( "(?<=,)[^\n\r]+(?=)", command )
        if len(layer_number) != 1:
            print "Syntax error while getting layer in POLY, line #%d" % current_line
            exit()
        poly_object["layer"] = int(layer_number[0])

        if poly_object["layer"] > 10 or poly_object["layer"] < 1 :
            print "Error on line %d - layer number should be in range [1, 10], found %d" % (current_line,
                                                                                            poly_object["layer"])
            exit()

        points_list = []
        #Get all points
        for iter in range(0, int(edges_count[0])):
            points_line = solution.readline()
            current_line += 1
            points = points_line.split(';')
            if len(points) != 2:
                print "Syntax error extracting POLY point, line #%d" % current_line
                exit()
            points_list.append( (float(points[0].replace(',', decimal_point)),
                                           float(points[1].replace(',', decimal_point))) )

    except:
        print "Syntax error, line #%d" % current_line
        exit()

    #Create shapely polygon
    poly_object["poly"] = Polygon( points_list )

    serve_route_table( poly_object )



def main():

    global current_line
    global route_table
    global jumps_count
    global jumps_list

    inputfile = sys.argv[1]

    #Load connect & coordinates files
    with open('coordinates.csv', 'rU') as fcoords:
        csvreader = reader( fcoords, delimiter=';' )
        for row in csvreader:
            if (int(row[1]) == 1):
                coordinates_mcu[int(row[0])] = Point(
                                     float(row[2].replace(',', decimal_point)),
                                     float(row[3].replace(',', decimal_point)) )
            else:
                coordinates_mem[int(row[0])] = Point(
                                     float(row[2].replace(',', decimal_point)),
                                     float(row[3].replace(',', decimal_point)) )

    with open('connect.csv', 'rU') as fcoords:
        csvreader = reader( fcoords, delimiter=';' )
        for row in csvreader:
            connect[int(row[0])] = int(row[1])

    #Load the solution file, create route table
    solution = open(inputfile, 'rU')
    while True:

        current_line += 1
        command = solution.readline()

        if command.startswith( 'POLY' ):
            parse_poly(command, solution)
        elif command.startswith( 'JUMP' ):
            jumps_count += 1
            try:
                point_x = re.findall("(?<=JUMP)[^;]+(?=;)", command)
                if len(point_x) != 1:
                    print "Syntax error extracting JUMP point X coordinate, line #%d" % current_line
                    exit()
                point_x = float(point_x[0].replace(',', decimal_point))
                point_y = re.findall("(?<=;)[^;]+(?=)", command)
                if len(point_y) != 1:
                    print "Syntax error extracting JUMP point Y coordinate, line #%d" % current_line
                    exit()
                point_y = float(point_y[0].replace(',', decimal_point))
                jumps_list.append( Point( point_x, point_y ) )
            except:
                print "Syntax error, line #%d" % current_line
                exit()

        if command == '':
            break

    serve_route_table_jump()

    correct_connections = {}

    #OK, checking connections are correct
    for pin_mcu, point_mcu in coordinates_mcu.iteritems():
        for route in route_table:
            for poly in route:
                if poly["poly"].intersects(point_mcu.buffer(0.1)) and poly["layer"] == 1:
                    for pin_mem, point_mem in coordinates_mem.iteritems():
                        if poly["poly"].intersects(point_mem.buffer(0.1)) and connect[pin_mcu] != pin_mem:
                            print "MCU pin %d and Memory pin %d are connected, though shouldn't" % (pin_mcu, pin_mem)
                        elif poly["poly"].contains(point_mem):
                            correct_connections[pin_mcu] = pin_mem
                    break

    #Printing points that are not connected, but should be
    for pin_mcu in range(1, 41):
        if not(correct_connections.has_key( pin_mcu )):
            print "MCU pin %d is NOT connected with Memory pin %d, though should" % (pin_mcu, connect[pin_mcu])

    #Printing estimation of electrical length
    el_length = 0.0
    for route in route_table:
        for poly in route:
            el_length += poly["poly"].length / 2.0

    print "S = %d" % el_length
    print "Vias %d" % len(jumps_list)

    #calculate layers used
    layers = 1
    for route in route_table:
        for poly in route:
            if poly["layer"] > layers:
                layers = poly["layer"]

    print "Layers used %d" % layers

main()