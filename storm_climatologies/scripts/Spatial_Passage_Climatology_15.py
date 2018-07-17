"""Spatial Passage Map """

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
MAX_LAT_DEG = 55.
MIN_LONG_DEG = 230.
MAX_LONG_DEG = 300.
LATITUDE_SPACING_DEG = .10 
LONGITUDE_SPACING_DEG = .10
NUM_ROWS = 1 + int(numpy.round((MAX_LAT_DEG - MIN_LAT_DEG) / LATITUDE_SPACING_DEG))
NUM_COLUMNS = 1 + int(numpy.round((MAX_LONG_DEG - MIN_LONG_DEG) / LONGITUDE_SPACING_DEG))
#Center point of MYRORRS Grid = 37.5 deg N and 265.0 deg E
CENTRAL_MAP_POINT_LAT= 37.5
CENTRAL_MAP_POINT_LONG= 265.0

X_SPACING_METRES = 10000.
Y_SPACING_METRES = 10000.

if __name__ == '__main__':
    spc_date_strings = time_conversion.get_spc_dates_in_range(
        first_spc_date_string=FIRST_SPC_DATE_STRING,
        last_spc_date_string=LAST_SPC_DATE_STRING)
    num_spc_dates = len(spc_date_strings)
    storm_object_table_by_spc_date = [None] * num_spc_dates

    grid_point_lat_, grid_point_long = utils.get_latlng_grid_points(min_latitude_deg=MIN_LAT_DEG, min_longitude_deg=MIN_LONG_DEG, 
                                                     lat_spacing_deg= LATITUDE_SPACING_DEG, lng_spacing_deg=LONGITUDE_SPACING_DEG,
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
        date_in_memory_indices = utils._get_dates_needed(working_date_index=working_date_index, num_dates=num_spc_dates,
            climatology_type=PASSAGE_CLIMATOLOGY_TYPE)
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
        
    #this is the part that initializes the grid array        
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
        multiday_storm_object_table = multiday_storm_object_table[multiday_storm_object_table['age_sec']>= 900]
        multiday_storm_object_table= multiday_storm_object_table.reset_index()
        del multiday_storm_object_table['index']
        centroids_x = numpy.array([multiday_storm_object_table.loc[x]['centroid_x_metres'] for x in range(0,len(multiday_storm_object_table))])
        centroids_y = numpy.array([multiday_storm_object_table.loc[y]['centroid_y_metres'] for y in range(0,len(multiday_storm_object_table))])
        
        
        
        utils._bin_storm_objects_one_for_loop(centroids_x, centroids_y, unique_grid_point_x_metres,
                                       unique_grid_point_y_metres, grid_cell_count_matrix)
    grid_cell_count_matrix = numpy.ma.masked_where(grid_cell_count_matrix == 0, grid_cell_count_matrix)
