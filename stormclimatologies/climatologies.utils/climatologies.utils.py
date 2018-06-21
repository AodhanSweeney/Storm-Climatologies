"""This module gets specified dates for files that should be read and written in. This also developes the 
concatonated storm object table"""
import numpy
import pandas
from gewittergefahr.gg_utils import time_conversion
from gewittergefahr.gg_io import storm_tracking_io as tracking_io


#sample dates for one day of April 15th 2011
FIRST_SPC_DATE_STRING = '20110415'
LAST_SPC_DATE_STRING = '20110415'
#wherever the data is stored
TOP_PROCESSED_DIR_NAME = '/Users/reu/Downloads/'
TRACKING_SCALE_METRES2 = 314159265

BIRTH_CLIMATOLOGY_TYPE = 'birth'
DEATH_CLIMATOLOGY_TYPE = 'death'
PASSAGE_CLIMATOLOGY_TYPE = 'passage'

spc_date_strings = time_conversion.get_spc_dates_in_range(first_spc_date_string=FIRST_SPC_DATE_STRING,
                                                          last_spc_date_string=LAST_SPC_DATE_STRING)
num_spc_dates = len(spc_date_strings)
storm_object_table_by_spc_date = [None] * num_spc_dates


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

  
def get_storm_object_table(num_spc_dates, climatology_type, working_date_index):
    date_in_memory_indices = _get_dates_needed(working_date_index, num_spc_dates, climatology_type)
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
    multiday_storm_object_table = multiday_storm_object_table[multiday_storm_object_table['age_sec']>= 900]
    return multiday_storm_object_table

  
def get_the_centroid(multiday_storm_object_table, address_of_unique_storms):
    """turns the shapely point list of centroids taken from the multiday storm object table
    and converts them into a numpy array
    listarray = []
    for pp in mypoints:
        listarray.append([pp.x, pp.y])
    nparray = np.array(listarray)"""

    centroids = []
    for i in address_of_unique_storms:
        polygons = multiday_storm_object_table.loc[i]
        centroid_pt = polygons.centroid
        centroids.append([centroid_pt.x, centroid_pt.y])
    return numpy.array(centroids)

  
def get_latlng_grid_points(min_latitude_deg=None, min_longitude_deg=None,
                           lat_spacing_deg=None, lng_spacing_deg=None,
                           num_rows=None, num_columns=None):
    """Generates unique lat and long of grid points in regular lat-long grid.
    M = number of rows in grid
    N = number of columns in grid
    :param min_latitude_deg: Minimum latitude over all grid points (deg N).
    :param min_longitude_deg: Minimum longitude over all grid points (deg E).
    :param lat_spacing_deg: Meridional spacing between adjacent grid points.
        Alternate interpretation: length of each grid cell in N-S direction.
    :param lng_spacing_deg: Zonal spacing between adjacent grid points.
        Alternate interpretation: length of each grid cell in E-W direction.
    :param num_rows: Number of rows (unique grid-point latitudes) in grid.
    :param num_columns: Number of columns (unique grid-point longitudes) in
        grid.
    :return: grid_point_latitudes_deg: length-M numpy array with latitudes of
        grid points (deg N).
    :return: grid_point_longitudes_deg: length-N numpy array with longitudes of
        grid points (deg E).
    """

    error_checking.assert_is_valid_latitude(min_latitude_deg)
    min_longitude_deg = lng_conversion.convert_lng_positive_in_west(
        min_longitude_deg, allow_nan=False)
    error_checking.assert_is_greater(lat_spacing_deg, 0.)
    error_checking.assert_is_greater(lng_spacing_deg, 0.)
    error_checking.assert_is_integer(num_rows)
    error_checking.assert_is_greater(num_rows, 0)
    error_checking.assert_is_integer(num_columns)
    error_checking.assert_is_greater(num_columns, 0)

    max_latitude_deg = min_latitude_deg + (num_rows - 1) * lat_spacing_deg
    max_longitude_deg = min_longitude_deg + (num_columns - 1) * lng_spacing_deg

    grid_point_latitudes_deg = numpy.linspace(min_latitude_deg,
                                              max_latitude_deg, num=num_rows)
    grid_point_longitudes_deg = numpy.linspace(min_longitude_deg,
                                               max_longitude_deg,
                                               num=num_columns)

    return grid_point_latitudes_deg, grid_point_longitudes_deg

  
def latlng_vectors_to_matrices(unique_latitudes_deg, unique_longitudes_deg):
    """Converts vectors of lat and long coordinates to matrices.
    This method works only for a regular lat-long grid.  Works for coordinates
    of either grid points or grid-cell edges.
    M = number of rows in grid
    N = number of columns in grid
    :param unique_latitudes_deg: length-M numpy array with latitudes (deg N) of
        either grid points or grid-cell edges.
    :param unique_longitudes_deg: length-N numpy array with longitudes (deg E)
        of either grid points or grid-cell edges.
    :return: latitude_matrix_deg: M-by-N numpy array, where
        latitude_matrix_deg[i, *] = unique_latitudes_deg[i].  Each column in
        this matrix is the same.
    :return: longitude_matrix_deg: M-by-N numpy array, where
        longitude_matrix_deg[*, j] = unique_longitudes_deg[j].  Each row in this
        matrix is the same.
    """

    error_checking.assert_is_valid_lat_numpy_array(unique_latitudes_deg)
    error_checking.assert_is_numpy_array(unique_latitudes_deg, num_dimensions=1)
    error_checking.assert_is_numpy_array(unique_longitudes_deg,
                                         num_dimensions=1)
    unique_longitudes_deg = lng_conversion.convert_lng_positive_in_west(
        unique_longitudes_deg, allow_nan=False)

    (longitude_matrix_deg, latitude_matrix_deg) = numpy.meshgrid(
        unique_longitudes_deg, unique_latitudes_deg)
    return latitude_matrix_deg, longitude_matrix_deg
  
  
  def distance_from_latlng(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    # Radius of earth in kilometers is 6371
    km = 6371* c
    return km
