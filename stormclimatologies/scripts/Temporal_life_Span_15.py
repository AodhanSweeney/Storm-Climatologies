import numpy
import pandas
from gewittergefahr.gg_io import storm_tracking_io as tracking_io
from gewittergefahr.gg_utils import time_conversion
import matplotlib.pyplot as plt


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


if __name__ == '__main__':
    spc_date_strings = time_conversion.get_spc_dates_in_range(
        first_spc_date_string=FIRST_SPC_DATE_STRING,
        last_spc_date_string=LAST_SPC_DATE_STRING)
    num_spc_dates = len(spc_date_strings)

    storm_object_table_by_spc_date = [None] * num_spc_dates
    storm_life_times = []
    storm_long_lives = []

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
        multiday_storm_object_table = multiday_storm_object_table[multiday_storm_object_table['age_sec'] >= 900]
        multiday_storm_object_table= multiday_storm_object_table.reset_index()
        del multiday_storm_object_table['index']        

        storm_switch = multiday_storm_object_table.reindex(index=multiday_storm_object_table.index[::-1])

        deaths_table = storm_switch['storm_id'].values

        last_table, lastplace_holder= numpy.unique(deaths_table, return_index = True)
        addresses_of_unique_storms = []
        for x in lastplace_holder:
            if ((max(multiday_storm_object_table['unix_time_sec']) - 86800)<= 
                multiday_storm_object_table.loc[x]['unix_time_sec']
                <= max(multiday_storm_object_table['unix_time_sec'])):
                addresses_of_unique_storms.append(x)

        storm_ages = []
        for x in addresses_of_unique_storms:
            storm_ages.append(multiday_storm_object_table.loc[x]['age_sec'])
        #print(Storm_life_times)
        print(SEPARATOR_STRING)
        
        for x in range(0,len(storm_ages)):
            if storm_ages[x] == 0:
                storm_life_times.append(storm_ages[x])
                instantaneous_storms.append(storm_ages[x])
            if 0< storm_ages[x] <=43200:
                storm_life_times.append(storm_ages[x])
            if storm_ages[x]> 43201:
                storm_long_lives.append(storm_ages[x])
        

    print('Storms lasting longer than 12 hours', len(storm_long_lives))
    print('mean life time', numpy.mean(storm_life_times))
    print('standard deviation', numpy.std(storm_life_times))
    plt.hist(storm_life_times, bins = 'auto')   
    plt.title('Storm Life Time Data April 2011')
    plt.xlabel('Life Time in seconds')
    plt.ylabel('Frequency')
    plt.show()
