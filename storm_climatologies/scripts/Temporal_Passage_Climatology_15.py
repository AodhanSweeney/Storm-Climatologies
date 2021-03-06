import numpy
import pandas
from gewittergefahr.gg_io import storm_tracking_io as tracking_io
from gewittergefahr.gg_utils import time_conversion
import matplotlib.pyplot as plt
import utils

SEPARATOR_STRING = '\n\n' + '*' * 50 + '\n\n'

FIRST_SPC_DATE_STRING = '20110401'
LAST_SPC_DATE_STRING = '20110401'
TOP_PROCESSED_DIR_NAME = '/users/reu/Downloads'
TRACKING_SCALE_METRES2 = 314159265

HOUR_FORMAT = '%H'
NUM_HOURS_PER_DAY = 24

BIRTH_CLIMATOLOGY_TYPE = 'birth'
DEATH_CLIMATOLOGY_TYPE = 'death'
PASSAGE_CLIMATOLOGY_TYPE = 'passage'


def _get_storm_id_and_hour_strings(storm_ids, unix_times_sec):
    """Turns each pair of storm ID and time into string with storm ID and hour.

    N = number of storm objects

    :param storm_ids: length-N list of storm IDs (strings).
    :param unix_times_sec: length-N numpy array of valid times.
    :return: storm_id_and_hour_strings: length-N list of strings.
    """

    hour_strings = [time_conversion.unix_sec_to_string(t, HOUR_FORMAT)
                    for t in unix_times_sec]

    return ['{0:s}_{1:s}'.format(storm_ids[i], hour_strings[i])
            for i in range(len(storm_ids))]


def _parse_storm_id_and_hour_strings(storm_id_and_hour_strings):
    """Parses hour from each string created by `_get_storm_id_and_hour_strings`.

    N = number of storm objects

    :param storm_id_and_hour_strings: length-N list of strings created by
        `_get_storm_id_and_hour_strings`.
    :return: hour_integers: length-N numpy array of hours.
    """

    hour_strings = [s.split('_')[-1] for s in storm_id_and_hour_strings]
    return numpy.array([int(s) for s in hour_strings], dtype=int)


if __name__ == '__main__':
    spc_date_strings = time_conversion.get_spc_dates_in_range(
        first_spc_date_string=FIRST_SPC_DATE_STRING,
        last_spc_date_string=LAST_SPC_DATE_STRING)
    num_spc_dates = len(spc_date_strings)

    storm_object_table_by_spc_date = [None] * num_spc_dates
    num_storm_objects_by_hour = numpy.full(NUM_HOURS_PER_DAY, 0, dtype=int)

    for working_date_index in range(num_spc_dates):
        mutliday_storm_object_table = get_storm_object_table(num_spc_dates, Passage_Climatology, working_date_index)

        print SEPARATOR_STRING

        for j in date_in_memory_indices[1:]:
            storm_object_table_by_spc_date[j], _ = (
                storm_object_table_by_spc_date[j].align(
                    storm_object_table_by_spc_date[date_in_memory_indices[0]],
                    axis=1))

        storm_object_tables_to_concat = [storm_object_table_by_spc_date[j] for j in date_in_memory_indices]
        multiday_storm_object_table = pandas.concat(storm_object_tables_to_concat, axis=0, ignore_index=True)
        multiday_storm_object_table = multiday_storm_object_table[multiday_storm_object_table['age_sec'] >= 900]


        
  
        storm_id_and_hour_strings = _get_storm_id_and_hour_strings(
                        storm_ids=multiday_storm_object_table['storm_id'].values,
                        unix_times_sec=multiday_storm_object_table['unix_time_sec'].values)
    
        
        
        unique_storm_id_and_hour_strings = set(storm_id_and_hour_strings)
        storm_object_hours = _parse_storm_id_and_hour_strings(unique_storm_id_and_hour_strings)

        unique_hours, unique_hour_counts = numpy.unique(storm_object_hours, return_counts=True)
    
        for j in range(len(unique_hours)):
            num_storm_objects_by_hour[unique_hours[j]] += unique_hour_counts[j]
            print ('Hour = {0:d} ... number of storm objects on date "{1:s}" = '
                    '{2:d} ... number of storm objects total = {3:d}'
                    ).format(unique_hours[j], spc_date_strings[working_date_index],unique_hour_counts[j],
                     num_storm_objects_by_hour[unique_hours[j]])
        print SEPARATOR_STRING

    plt.bar(range(0,24),num_storm_objects_by_hour)
    plt.title('Storms By Hour Over CONUS April 2011')
    plt.xlabel("Hour of Day UTC time")
    plt.ylabel("Number of storms counted")
    plt.savefig('/Users/reu/Desktop/The Chart')
