import numpy
import pandas
from gewittergefahr.gg_io import storm_tracking_io as tracking_io
from gewittergefahr.gg_utils import time_conversion
import matplotlib.pyplot as plt
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
    storm_life_times = []
    storm_long_lives = []

    for working_date_index in range(num_spc_dates):
        mutliday_storm_object_table= utils.get_storm_object_table(num_spc_dates, Birth_Climatology, working_date_index)
        multiday_storm_object_table= multiday_storm_object_table.reset_index()
        del multiday_storm_object_table['index']        

        storm_switch = multiday_storm_object_table.reindex(index=multiday_storm_object_table.index[::-1])

        deaths_table = storm_switch['storm_id'].values

        last_table, lastplace_holder= numpy.unique(deaths_table, return_index = True)
        addresses_of_unique_storms = []
        for x in lastplace_holder:
            if ((max(multiday_storm_object_table['unix_time_sec']) - 86400)<= 
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
