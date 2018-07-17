import numpy
import pandas
from mpl_toolkits.basemap import Basemap
from gewittergefahr.gg_io import storm_tracking_io as tracking_io
from gewittergefahr.gg_utils import time_conversion
import matplotlib.pyplot as plt
from gewittergefahr.gg_utils import longitude_conversion as lng_conversion
from gewittergefahr.gg_utils import error_checking
import utils

DEGREES_LAT_TO_METRES = 60 * 1852
DEGREES_TO_RADIANS = numpy.pi / 180

FIRST_SPC_DATE_STRING = '20110401'
LAST_SPC_DATE_STRING = '20110401'
TOP_PROCESSED_DIR_NAME = '/Users/reu/Downloads/'
TRACKING_SCALE_METRES2 = 314159265
Sep_String = '*'*50

BIRTH_CLIMATOLOGY_TYPE = 'birth'
DEATH_CLIMATOLOGY_TYPE = 'death'
PASSAGE_CLIMATOLOGY_TYPE = 'passage'

MIN_LAT_DEG = 20.
MIN_LONG_DEG = 230.
LATITUDE_SPACING_DEG = 0.1 
LONGITUDE_SPACING_DEG = 0.1
NUM_ROWS = 350
NUM_COLUMNS = 600

def _find_nearest_value(sorted_input_values, test_value):
    """Finds nearest value in array to test value.

    This method is based on the following:

    https://stackoverflow.com/posts/26026189/revisions

    :param sorted_input_values: 1-D numpy array.  Must be sorted in ascending
        order.
    :param test_value: Test value.
    :return: nearest_value: Nearest value in `sorted_input_values` to
        `test_value`.
    :return: nearest_index: Array index of nearest value.
    """

    nearest_index = numpy.searchsorted(
        sorted_input_values, test_value, side='left')

    subtract_one = nearest_index > 0 and (
        nearest_index == len(sorted_input_values) or
        math.fabs(test_value - sorted_input_values[nearest_index - 1]) <
        math.fabs(test_value - sorted_input_values[nearest_index]))
    if subtract_one:
        nearest_index -= 1

    return sorted_input_values[nearest_index], nearest_index

def _bin_storm_objects_one_for_loop(
        storm_centroids_x_metres, storm_centroids_y_metres,
        unique_grid_point_x_metres, unique_grid_point_y_metres, grid_cell_count_matrix):
    """Counts number of storm objects in each grid cell, using single for-loop.

    :param storm_centroids_x_metres: See doc for
        `_bin_storm_objects_triple_for_loop`.
    :param storm_centroids_y_metres: Same.
    :param unique_grid_point_x_metres: Same.
    :param unique_grid_point_y_metres: Same.
    :return: grid_cell_count_matrix: Same.
    """

    num_storm_objects = len(storm_centroids_x_metres)
    num_grid_rows = len(unique_grid_point_y_metres)
    num_grid_columns = len(unique_grid_point_x_metres)

    for i in range(num_storm_objects):
        _, this_row = _find_nearest_value(
            unique_grid_point_y_metres, storm_centroids_y_metres[i])
        _, this_column = _find_nearest_value(
            unique_grid_point_x_metres, storm_centroids_x_metres[i])
        grid_cell_count_matrix[this_row, this_column] += 1

    return grid_cell_count_matrix



if __name__ == '__main__':
    spc_date_strings = time_conversion.get_spc_dates_in_range(
        first_spc_date_string=FIRST_SPC_DATE_STRING,
        last_spc_date_string=LAST_SPC_DATE_STRING)
    num_spc_dates = len(spc_date_strings)

    grid_point_lat_, grid_point_long = get_latlng_grid_points(min_latitude_deg=MIN_LAT_DEG, min_longitude_deg=MIN_LONG_DEG, 
                                                                lat_spacing_deg=LATITUDE_SPACING_DEG, 
                                                                lng_spacing_deg=LONGITUDE_SPACING_DEG, 
                                                                num_rows=NUM_ROWS, num_columns=NUM_COLUMNS)
    
    grid_point_lat = numpy.flip(grid_point_lat_,-1)
    lats, lons = latlng_vectors_to_matrices(grid_point_lat, grid_point_long)
    central_latitude_deg = numpy.mean(numpy.array([MIN_LAT_DEG, MAX_LAT_DEG]))
    central_longitude_deg = numpy.mean(numpy.array([MIN_LONG_DEG, MAX_LONG_DEG]))
     
    projection_object = projections.init_azimuthal_equidistant_projection(central_latitude_deg=central_latitude_deg,
                                                                          central_longitude_deg=central_longitude_deg)
    # Project lat-long grid points to x-y. 
    (grid_point_x_matrix_metres, grid_point_y_matrix_metres) = projections.project_latlng_to_xy(
                                                                                latitudes_deg=lats,
                                                                                longitudes_deg=lons,
                                                                                projection_object=projection_object)    
    
    x_min_metres = numpy.min(grid_point_x_matrix_metres)
    x_max_metres = numpy.max(grid_point_x_matrix_metres)
    y_min_metres = numpy.min(grid_point_y_matrix_metres)
    y_max_metres = numpy.max(grid_point_y_matrix_metres)
    
    # Round corners to nearest 10 km.  These will become the corners of the actual
    # x-y grid.
    x_min_metres = number_rounding.floor_to_nearest(x_min_metres, X_SPACING_METRES)
    x_max_metres = number_rounding.ceiling_to_nearest(x_max_metres, X_SPACING_METRES)
    y_min_metres = number_rounding.floor_to_nearest(y_min_metres, Y_SPACING_METRES)
    y_max_metres = number_rounding.ceiling_to_nearest(y_max_metres, Y_SPACING_METRES)

    num_grid_rows = 1 + int(numpy.round((y_max_metres - y_min_metres) / Y_SPACING_METRES))
    num_grid_columns = 1 + int(numpy.round((x_max_metres - x_min_metres) / X_SPACING_METRES))
    (unique_grid_point_x_metres, unique_grid_point_y_metres) = grids.get_xy_grid_points(
                                                                x_min_metres=x_min_metres, 
                                                                y_min_metres=y_min_metres,
                                                                x_spacing_metres=X_SPACING_METRES, 
                                                                y_spacing_metres=Y_SPACING_METRES,
                                                                num_rows=num_grid_rows, num_columns=num_grid_columns)    
    
    
    (grid_point_x_matrix_metres, grid_point_y_matrix_metres) = grids.xy_vectors_to_matrices(
                                                                x_unique_metres=unique_grid_point_x_metres,
                                                                y_unique_metres=unique_grid_point_y_metres)
    
    storm_object_table_by_spc_date = [None] * num_spc_dates
    num_grid_rows = len(unique_grid_point_y_metres)
    num_grid_columns = len(unique_grid_point_x_metres)    
    
    grid_cell_count_matrix = numpy.full((num_grid_rows, num_grid_columns), 0, dtype=int)
    
    for working_date_index in range(num_spc_dates):
        date_in_memory_indices = _get_dates_needed(working_date_index=working_date_index, num_dates=num_spc_dates,
            climatology_type=BIRTH_CLIMATOLOGY_TYPE)
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
        
        for j in date_in_memory_indices[1:]:
            storm_object_table_by_spc_date[j], _ = (storm_object_table_by_spc_date[j].align(
                                                    storm_object_table_by_spc_date[date_in_memory_indices[0]], axis=1))
        storm_object_tables_to_concat = [storm_object_table_by_spc_date[j] for j in date_in_memory_indices]
        multiday_storm_object_table = pandas.concat(storm_object_tables_to_concat, axis=0, ignore_index=True)
        centroids_x_metres, centroids_y_metres = projections.project_latlng_to_xy(
                                latitudes_deg=multiday_storm_object_table[tracking_utils.CENTROID_LAT_COLUMN].values,
                                longitudes_deg=multiday_storm_object_table[tracking_utils.CENTROID_LNG_COLUMN].values,
                                projection_object=projection_object)
        
        argument_dict = {'centroid_x_metres': centroids_x_metres, 'centroid_y_metres': centroids_y_metres}
        multiday_storm_object_table = multiday_storm_object_table.assign(**argument_dict)
#lets change our storm object table to make it so that we only take storms that last 900 seconds or more
        mature_storm_table = multiday_storm_object_table[multiday_storm_object_table['age_sec']>= 900]
        mature_storm_ids = mature_storm_table['storm_id'].values
        print('total storm objects', len(multiday_storm_object_table))

        multi_storm_ids, place_holder = numpy.unique(multiday_storm_object_table['storm_id'].values, 
                                                     return_index = True)
        
#now that we have all the places of births regardlesss of age, if the name of that birth is in mature_storm_table
#return the starting position of the storm
        initial_storm_address = []
        for x in place_holder:
            if multiday_storm_object_table.loc[x]['storm_id'] in mature_storm_ids:
                initial_storm_address.append(x)

    
    
    
        unique_times = [multiday_storm_object_table.loc[x]['unix_time_sec'] for x in initial_storm_address]
        address_of_interest = []
        for x in initial_storm_address:
            if multiday_storm_object_table.loc[x]['unix_time_sec'] >= (max(multiday_storm_object_table['unix_time_sec']) - 86400):
                address_of_interest.append(x)


        centroids_x = numpy.array([multiday_storm_object_table.loc[x]['centroid_x_metres'] for x in address_of_interest])
        centroids_y = numpy.array([multiday_storm_object_table.loc[y]['centroid_y_metres'] for y in address_of_interest])

        
        _bin_storm_objects_one_for_loop(centroids_x, centroids_y, unique_grid_point_x_metres,
                                       unique_grid_point_y_metres, grid_cell_count_matrix)
    
#apply mask so that grid cells that are have no storm births become nans
    grid_cell_count_matrix = numpy.ma.masked_where(grid_cell_count_matrix == 0, grid_cell_count_matrix)
