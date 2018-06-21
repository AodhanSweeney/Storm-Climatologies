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


def _get_storm_id_and_hour_strings(storm_ids, unix_times_sec):
    """Turns each pair of storm ID and time into string with storm ID and hour.

    N = number of storm objects

    :param storm_ids: length-N list of storm IDs (strings).
    :param unix_times_sec: length-N numpy array of valid times.
    :return: storm_id_and_hour_strings: length-N list of strings.
    """
    hour_strings = [time_conversion.unix_sec_to_string(t, HOUR_FORMAT)
                    for t in unix_times_sec]

    return ['{0:s}_{1:s}'.format( hour_strings[i])
            for i in range(len(storm_ids))]

def storm_id(storm_id):
    """Parses hour from each string created by `_get_storm_id_and_hour_strings`.

    N = number of storm objects

    :param storm_id_and_hour_strings: length-N list of strings created by
        `_get_storm_id_and_hour_strings`.
    :return: hour_integers: length-N numpy array of hours.
    """
    storm_strings = []
    for s in storm_id:
        storm_strings.append(s)
    
    return numpy.array(storm_strings)


if __name__ == '__main__':
    spc_date_strings = time_conversion.get_spc_dates_in_range(
        first_spc_date_string=FIRST_SPC_DATE_STRING,
        last_spc_date_string=LAST_SPC_DATE_STRING)
    num_spc_dates = len(spc_date_strings)

    storm_object_table_by_spc_date = [None] * num_spc_dates
    storm_object_areas = []

    for working_date_index in range(num_spc_dates):
        date_in_memory_indices = _get_dates_needed(working_date_index=working_date_index, num_dates=num_spc_dates)
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


        #storm_ids = storm_id(multiday_storm_object_table['storm_id'])
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