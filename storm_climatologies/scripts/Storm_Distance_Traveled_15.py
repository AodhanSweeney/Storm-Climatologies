"""Looking now at the distance traveled between the storm over its life time. Take initial centroid position
and final centroid position and find the distance between them. """

import numpy
import pandas
from gewittergefahr.gg_io import storm_tracking_io as tracking_io
from gewittergefahr.gg_utils import time_conversion
import matplotlib.pyplot as plt
import pyproj    
import shapely
import shapely.ops as ops
from shapely.geometry.polygon import Polygon
from functools import partial
from shapely.ops import transform
from math import radians, cos, sin, asin, sqrt
import utils

SEPARATOR_STRING = '\n\n' + '*' * 50 + '\n\n'

FIRST_SPC_DATE_STRING = '20110401'
LAST_SPC_DATE_STRING = '20110430'
TOP_PROCESSED_DIR_NAME = '/Users/reu/Downloads/'
TRACKING_SCALE_METRES2 = 314159265

HOUR_FORMAT = '%H'
NUM_HOURS_PER_DAY = 24

BIRTH_CLIMATOLOGY_TYPE = 'birth'
DEATH_CLIMATOLOGY_TYPE = 'death'
PASSAGE_CLIMATOLOGY_TYPE = 'passage'

    
    storm_object_table_by_spc_date = [None] * num_spc_dates
    
    distance_in_km = []

    for working_date_index in range(num_spc_dates):
        multiday_storm_object_table = get_storm_object_table(num_spc_dates, Birth_Climatology, working_date_index)
        multiday_storm_object_table= multiday_storm_object_table.reset_index()
        del multiday_storm_object_table['index']

        storm_id_birth = multiday_storm_object_table['storm_id'].values
        print('total storm objects', len(storm_id_birth))
        first_table, firstplace_holder = numpy.unique(storm_id_birth, return_index = True)
        
        storm_switch = multiday_storm_object_table.reindex(index=multiday_storm_object_table.index[::-1])
        storm_id_death = storm_switch['storm_id'].values
        
        last_table, lastplace_holder= numpy.unique(storm_id_death, return_index = True)
        first_address = []
        last_address = []
        for x in firstplace_holder:
            for y in lastplace_holder:
                if (storm_id_birth[x]) == (storm_id_death[y]):
                    first_address.append(x)
                    last_address.append(y)
        
        first_occurance_position = utils.get_the_centroid(multiday_storm_object_table['polygon_object_latlng'], first_address)
        last_occurance_position = utils.get_the_centroid(multiday_storm_object_table['polygon_object_latlng'], last_address)
        for x in range(0,len(first_occurance_position)):
            distance = utils.haversine(first_occurance_position[x,0], first_occurance_position[x,1], 
                  last_occurance_position[x,0], last_occurance_position[x,1])
            distance_in_km.append(distance)
    
    distances = numpy.array(distance_in_km)
    

    print('mean distance traveled (km)', numpy.mean(distances))
    print('standard deviation (km)', numpy.std(distances))
    print('median distance traveled (km)', numpy.median(distances))
    plt.hist(distances, bins = 'auto')   
    plt.title('Storm Distance Traveled Data April 2011')
    plt.xlabel('Distance Traveled in km')
    plt.ylabel('Frequency')
    plt.show()
