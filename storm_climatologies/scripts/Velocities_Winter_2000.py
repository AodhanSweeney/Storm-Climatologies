import numpy
import pandas
from gewittergefahr.gg_io import storm_tracking_io as tracking_io
from gewittergefahr.gg_utils import time_conversion

SEPARATOR_STRING = '\n\n' + '*' * 50 + '\n\n'

FIRST_SPC_DATE_STRING = '20000103'
LAST_SPC_DATE_STRING = '20000228'
TOP_PROCESSED_DIR_NAME = '/condo/swatwork/ralager/myrorss_40dbz_echo_tops/final_tracks/reanalyzed/'
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
    Total_EV_List =[]
    Total_NV_List =[]
    for working_date_index in range(num_spc_dates):
        date_in_memory_indices = utils._get_dates_needed(
            working_date_index=working_date_index, num_dates=num_spc_dates,
            climatology_type=PASSAGE_CLIMATOLOGY_TYPE)

        for i in range(num_spc_dates):
            if i in date_in_memory_indices:
                if storm_object_table_by_spc_date[i] is None:

                    # Find tracking files for [i]th date.
                    these_tracking_file_names = (
                        tracking_io.find_processed_files_one_spc_date(
                            spc_date_string=spc_date_strings[i],
                            data_source='segmotion',
                            top_processed_dir_name=TOP_PROCESSED_DIR_NAME,
                            tracking_scale_metres2=TRACKING_SCALE_METRES2))

                    # Read tracking files for [i]th date.
                    storm_object_table_by_spc_date[i] = (
                        tracking_io.read_many_processed_files(
                            these_tracking_file_names))

                else:
                    print 'Clearing data for SPC date "{0:s}"...'.format(
                        spc_date_strings[i])
                    storm_object_table_by_spc_date[i] = None

        print SEPARATOR_STRING

        for j in date_in_memory_indices[1:]:
            storm_object_table_by_spc_date[j], _ = (
                storm_object_table_by_spc_date[j].align(
                    storm_object_table_by_spc_date[date_in_memory_indices[0]],
                    axis=1))

        storm_object_tables_to_concat = [storm_object_table_by_spc_date[j] for j in date_in_memory_indices]
        multiday_storm_object_table = pandas.concat(storm_object_tables_to_concat, axis=0, ignore_index=True)
        mature_table = multiday_storm_object_table[multiday_storm_object_table['age_sec']>=900]
        storms = []
        for x in multiday_storm_object_table['storm_id']:
            if x in list(mature_table['storm_id']):
                storms.append(x)
        for y in storms:
            one_storm_table = multiday_storm_object_table[multiday_storm_object_table['storm_id'] ==y]
            EV_mean = numpy.mean(one_storm_table['east_velocity_m_s01'].values)
            NV_mean = numpy.mean(one_storm_table['north_velocity_m_s01'].values)
            Total_EV_List.append(EV_mean)
            Total_NV_List.append(NV_mean)

    numpy.save('/home/aodhan/MATRIX/EV_Winter_2000', Total_EV_List)
    numpy.save('/home/aodhan/MATRIX/NV_Winter_2000', Total_NV_List)
