import numpy
import pandas
from gewittergefahr.gg_io import storm_tracking_io as tracking_io
from gewittergefahr.gg_utils import time_conversion
import matplotlib.pyplot as plt
plt.switch_backend('agg')
import pyproj    
import shapely.ops as ops
from functools import partial
import utils


SEPARATOR_STRING = '\n\n' + '*' * 50 + '\n\n'

FIRST_SPC_DATE_STRING = '20000901'
LAST_SPC_DATE_STRING = '20001130'
TOP_PROCESSED_DIR_NAME = '/condo/swatwork/ralager/myrorss_40dbz_echo_tops/final_tracks/reanalyzed/'
TRACKING_SCALE_METRES2 = 314159265

OUR_FORMAT = '%H'
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
        date_in_memory_indices = utils._get_dates_needed(working_date_index=working_date_index, num_dates=num_spc_dates)
        for i in range(num_spc_dates):
            if i in date_in_memory_indices:
                if storm_object_table_by_spc_date[i] is None:
                    these_tracking_file_names = (tracking_io.find_processed_files_one_spc_date(
                                                    spc_date_string=spc_date_strings[i],
                                                    data_source='segmotion',
                                                    top_processed_dir_name=TOP_PROCESSED_DIR_NAME,
                                                    tracking_scale_metres2=TRACKING_SCALE_METRES2))
                    storm_object_table_by_spc_date[i] = (tracking_io.read_many_processed_files(
                                                        these_tracking_file_names))
            else:
                print 'Clearing data for SPC date "{0:s}"...'.format(spc_date_strings[i])
                storm_object_table_by_spc_date[i] = None
        
        print SEPARATOR_STRING

        for j in date_in_memory_indices[1:]:
            storm_object_table_by_spc_date[j], _ = (storm_object_table_by_spc_date[j].align(
                                                    storm_object_table_by_spc_date[date_in_memory_indices[0]], axis=1))

        storm_object_tables_to_concat = [storm_object_table_by_spc_date[j] for j in date_in_memory_indices]
        multiday_storm_object_table = pandas.concat(storm_object_tables_to_concat, axis=0, ignore_index=True)  
        multiday_storm_object_table = multiday_storm_object_table[multiday_storm_object_table['age_sec'] > 900]

        maxtime = max(multiday_storm_object_table['unix_time_sec'])

        new_storms = multiday_storm_object_table[multiday_storm_object_table['unix_time_sec']>= (maxtime-86400)]       
        storm_ids = new_storms['storm_id'].values
        unique_storms, unique_storm_adress = numpy.unique(storm_ids, return_index=True)
        new_storms = pandas.DataFrame(new_storms)
        new_storms= new_storms.reset_index()
        del new_storms['index']
        for x in unique_storms:
            areas_for_each_id = []
            storms = new_storms[new_storms['storm_id']==x]
            latlngs = storms['polygon_object_latlng'].values
            for i in latlngs:
            
                geom = i
                geom_area = ops.transform(partial(pyproj.transform, pyproj.Proj(init='EPSG:4326'), 
                                                  pyproj.Proj(proj='aea', lat1=geom.bounds[1],
                                                              lat2=geom.bounds[3])), geom)
                areas_for_each_id.append(geom_area.area)
            areas_array = numpy.array(areas_for_each_id)
            max_area = numpy.amax(areas_array)
            storm_object_areas.append(max_area/1000000)
    numpy.save('/home/aodhan/MATRIX/Spatial_Expanse', storm_object_areas)
