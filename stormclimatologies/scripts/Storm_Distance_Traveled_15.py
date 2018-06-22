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

# TODO(aodhan): This code should work for passage, but you need to modify for
# birth and death.


def _get_dates_needed(working_date_index, num_dates):
    """Gets dates needed for the given working date.

    :param working_date_index: Array index for the day currently being worked
        on.
    :param num_dates: Number of dates total.
    :return: date_needed_indices: 1-D numpy array with indices of dates needed.
    """
    date_needed_indices = []
    if working_date_index == 0:
        date_needed_indices.append(working_date_index)
    if working_date_index != 0:
        date_needed_indices.append(working_date_index - 1)
        date_needed_indices.append(working_date_index)

        
    return numpy.array(date_needed_indices, dtype=int)


def distance_from_latlng(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    # Radius of earth in kilometers is 6371
    km = 6371* c
    return km

def get_the_centroid(multiday_storm_object_table, address_of_unique_storms):
    """turns the shapely point list of centroids taken from the multiday storm object table
    and converts them into a numpy array"""

    centroids = []
    for i in address_of_unique_storms:
        polygons = multiday_storm_object_table.loc[i]
        centroid_pt = polygons.centroid
        centroids.append([centroid_pt.x, centroid_pt.y])
    return numpy.array(centroids)

if __name__ == '__main__':
    spc_date_strings = time_conversion.get_spc_dates_in_range(
        first_spc_date_string=FIRST_SPC_DATE_STRING,
        last_spc_date_string=LAST_SPC_DATE_STRING)
    num_spc_dates = len(spc_date_strings)
    
    storm_object_table_by_spc_date = [None] * num_spc_dates
    
    distance_in_km = []

    for working_date_index in range(num_spc_dates):
        date_in_memory_indices = _get_dates_needed(working_date_index=working_date_index, num_dates=num_spc_dates)
        for i in range(num_spc_dates):
            if i in date_in_memory_indices:
                if storm_object_table_by_spc_date[i] is None:

                    # Find tracking files for [i]th date.
                    these_tracking_file_names = (tracking_io.find_processed_files_one_spc_date(
                                                    spc_date_string=spc_date_strings[i],
                                                    data_source='segmotion',
                                                    top_processed_dir_name=TOP_PROCESSED_DIR_NAME,
                                                    tracking_scale_metres2=TRACKING_SCALE_METRES2))

                    # Read tracking files for [i]th date.
                    storm_object_table_by_spc_date[i] = (tracking_io.read_many_processed_files(
                                                        these_tracking_file_names))

            else:
                print 'Clearing data for SPC date "{0:s}"...'.format(spc_date_strings[i])
                storm_object_table_by_spc_date[i] = None
        
        print SEPARATOR_STRING

#we must make all the dates have data tables aligned with that of the 0th date index, initialize at one and iterate


        for j in date_in_memory_indices[1:]:
            storm_object_table_by_spc_date[j], _ = (storm_object_table_by_spc_date[j].align(
                                                    storm_object_table_by_spc_date[date_in_memory_indices[0]], axis=1))

        storm_object_tables_to_concat = [storm_object_table_by_spc_date[j] for j in date_in_memory_indices]
        multiday_storm_object_table = pandas.concat(storm_object_tables_to_concat, axis=0, ignore_index=True)
        multiday_storm_object_table = multiday_storm_object_table[multiday_storm_object_table['age_sec'] > 900]
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
        
        first_occurance_position = get_the_centroid(multiday_storm_object_table['polygon_object_latlng'], first_address)
        last_occurance_position = get_the_centroid(multiday_storm_object_table['polygon_object_latlng'], last_address)
        for x in range(0,len(first_occurance_position)):
            distance = distance_from_latlng(first_occurance_position[x,0], first_occurance_position[x,1], 
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
