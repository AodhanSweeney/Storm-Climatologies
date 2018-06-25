import numpy
import pandas
from gewittergefahr.gg_io import storm_tracking_io as tracking_io
from gewittergefahr.gg_utils import time_conversion
import matplotlib.pyplot as plt
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


if __name__ == '__main__':
    spc_date_strings = time_conversion.get_spc_dates_in_range(
        first_spc_date_string=FIRST_SPC_DATE_STRING,
        last_spc_date_string=LAST_SPC_DATE_STRING)
    num_spc_dates = len(spc_date_strings)

    storm_object_table_by_spc_date = [None] * num_spc_dates
    num_storm_objects_by_hour = numpy.full(NUM_HOURS_PER_DAY, 0, dtype=int)

    for working_date_index in range(num_spc_dates):
        multiday_storm_object_table = utils.get_dates_needed(num_spc_dates, Death_Climatology, working_date_index)
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
            if (max(times_of_death) - 86400)<= x <= max(times_of_death):
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
