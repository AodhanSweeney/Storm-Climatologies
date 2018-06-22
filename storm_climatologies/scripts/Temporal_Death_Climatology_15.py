import numpy
import pandas
from gewittergefahr.gg_io import storm_tracking_io as tracking_io
from gewittergefahr.gg_utils import time_conversion
import matplotlib.pyplot as plt


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


def _get_dates_needed(working_date_index, num_dates, climatology_type):
    """Gets dates needed for the given working date.

    :param working_date_index: Array index for the day currently being worked
        on.
    :param num_dates: Number of dates total.
    :return: date_needed_indices: 1-D numpy array with indices of dates needed.
    """
    date_needed_indices = []
    if climatology_type == PASSAGE_CLIMATOLOGY_TYPE:
        return numpy.array([working_date_index], dtype=int)
    
    if climatology_type == BIRTH_CLIMATOLOGY_TYPE: 
        if working_date_index != 0:
            date_needed_indices.append(working_date_index - 1)
            date_needed_indices.append(working_date_index)
        else:
            date_needed_indices.append(working_date_index)
    
    if climatology_type == DEATH_CLIMATOLOGY_TYPE:
        if working_date_index != (num_dates - 1):
            date_needed_indices.append(working_date_index)
            date_needed_indices.append(working_date_index + 1)
        else:
            date_needed_indices.append(working_date_index)
    
    return numpy.array(date_needed_indices, dtype=int)


if __name__ == '__main__':
    spc_date_strings = time_conversion.get_spc_dates_in_range(
        first_spc_date_string=FIRST_SPC_DATE_STRING,
        last_spc_date_string=LAST_SPC_DATE_STRING)
    num_spc_dates = len(spc_date_strings)

    storm_object_table_by_spc_date = [None] * num_spc_dates
    num_storm_objects_by_hour = numpy.full(NUM_HOURS_PER_DAY, 0, dtype=int)

    for working_date_index in range(num_spc_dates):
        date_in_memory_indices = _get_dates_needed(working_date_index=working_date_index, num_dates=num_spc_dates,
            climatology_type=DEATH_CLIMATOLOGY_TYPE)
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
        print('total storm objects', len(multiday_storm_object_table))
        
        storm_switch = multiday_storm_object_table.reindex(index=multiday_storm_object_table.index[::-1])
      
        deaths_table = storm_switch['storm_id'].values
        multi_storm_ids, place_holder = numpy.unique(deaths_table, return_index = True)

        print('sift 1',len(place_holder))
        times_of_death = [multiday_storm_object_table.loc[x]['unix_time_sec'] for x in place_holder]

        deaths_in_last_day = []
        for x in times_of_death:
            if (max(times_of_death) - 86800)<= x <= max(times_of_death):
                deaths_in_last_day.append(x)
        
        print('sift 2',len(deaths_in_last_day))
        _hour_strings = [time_conversion.unix_sec_to_string(t, HOUR_FORMAT) for t in deaths_in_last_day]
        _hour_ints = [int(x) for x in _hour_strings]
        unique_hours, unique_hour_counts = numpy.unique(_hour_ints, return_counts=True)
        for j in range(len(unique_hours)):
            num_storm_objects_by_hour[unique_hours[j]] += unique_hour_counts[j]

            print (
                'Hour = {0:d} ... number of storm deaths on date "{1:s}" = '
                '{2:d} ... number of storm deaths total = {3:d}'
            ).format(unique_hours[j], spc_date_strings[working_date_index],
                     unique_hour_counts[j],
                     num_storm_objects_by_hour[unique_hours[j]])
            
        print SEPARATOR_STRING
    plt.bar(range(0,24),num_storm_objects_by_hour)
    plt.title('Storms Deaths by Hour Over CONUS April 2011')
    plt.xlabel("Hour of Day UTC time")
    plt.ylabel("Number of deaths counted")
