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

def _get_dates_needed(working_date_index, num_dates, climatology_type):
    """Gets dates needed for the given working date.

    :param working_date_index: Array index for the day currently being worked
        on.
    :param num_dates: Number of dates total.
    :return: date_needed_indices: 1-D numpy array with indices of dates needed.
    """

    if climatology_type == PASSAGE_CLIMATOLOGY_TYPE:
        return numpy.array([working_date_index], dtype=int)

    date_needed_indices = []
    if climatology_type == BIRTH_CLIMATOLOGY_TYPE and working_date_index != 0:
        date_needed_indices.append(working_date_index - 1)

    date_needed_indices.append(working_date_index)

    if (climatology_type == DEATH_CLIMATOLOGY_TYPE and
            working_date_index != num_dates - 1):
        date_needed_indices.append(working_date_index + 1)

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
    Total_EV_List =[]
    Total_NV_List =[]
    for working_date_index in range(num_spc_dates):
        date_in_memory_indices = _get_dates_needed(
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
        """multiday_storm_object_table= multiday_storm_object_table.reset_index()
        del multiday_storm_object_table['index']"""
        #display(multiday_storm_object_table)
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