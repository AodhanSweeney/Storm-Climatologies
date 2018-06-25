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
import utils

SEPARATOR_STRING = '\n\n' + '*' * 50 + '\n\n'

FIRST_SPC_DATE_STRING = '20110401'
LAST_SPC_DATE_STRING = '20110403'
TOP_PROCESSED_DIR_NAME = '/Users/reu/Downloads/'
TRACKING_SCALE_METRES2 = 314159265

HOUR_FORMAT = '%H'
NUM_HOURS_PER_DAY = 24

BIRTH_CLIMATOLOGY_TYPE = 'birth'
DEATH_CLIMATOLOGY_TYPE = 'death'
PASSAGE_CLIMATOLOGY_TYPE = 'passage'

if __name__ == '__main__':
    spc_date_strings = time_conversion.get_spc_dates_in_range(
        first_spc_date_string=FIRST_SPC_DATE_STRING,
        last_spc_date_string=LAST_SPC_DATE_STRING)
    num_spc_dates = len(spc_date_strings)

    storm_object_table_by_spc_date = [None] * num_spc_dates
    storm_object_areas = []

    for working_date_index in range(num_spc_dates):
        mutliday_storm_object_table = get_storm_object_table(num_spc_dates, Passage_Climatology, working_date_index)


        print('total storm objects', len(multiday_storm_object_table))
        new_storms = []
        for x in multiday_storm_object_table.index:
            if ((max(multiday_storm_object_table['unix_time_sec']) - 86800)
            <= multiday_storm_object_table.loc[x]['unix_time_sec']
            <= max(multiday_storm_object_table['unix_time_sec'])):
                new_storms.append(multiday_storm_object_table.loc[x])        
        storm_ids = [i['storm_id'] for i in new_storms]
        print('sift 1', len(storm_ids))
        unique_storms, unique_storm_adress = numpy.unique(storm_ids, return_index=True)
        print('sift 2', len(unique_storms))
        for x in unique_storms:
            areas_for_each_id = []
            for i in range(0,len(new_storms)):
                if x == new_storms[i]['storm_id']:
                    geom = new_storms[i]['polygon_object_latlng']
                    geom_area = ops.transform(
                    partial(pyproj.transform, pyproj.Proj(init='EPSG:4326'), pyproj.Proj(proj='aea',
                            lat1=geom.bounds[1],
                            lat2=geom.bounds[3])), geom)
                    areas_for_each_id.append(geom_area.area)
            areas_array = numpy.array(areas_for_each_id)
            max_area = numpy.amax(areas_array)
            storm_object_areas.append(max_area/1000000)

    print('mean max storm size', numpy.mean(storm_object_areas))
    print('standard deviation', numpy.std(storm_object_areas))
    plt.hist(storm_object_areas, bins = 'auto')   
    plt.title('Storm Size Data April 2011')
    plt.xlabel('Spatial Expanse in km squared')
    plt.ylabel('Frequency')
    plt.show()
