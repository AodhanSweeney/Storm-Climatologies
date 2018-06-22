import numpy
import pandas
from mpl_toolkits.basemap import Basemap
from gewittergefahr.gg_io import storm_tracking_io as tracking_io
from gewittergefahr.gg_utils import time_conversion
import matplotlib.pyplot as plt
from gewittergefahr.gg_utils import longitude_conversion as lng_conversion
from gewittergefahr.gg_utils import error_checking

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
    storm_object_table_by_spc_date = [None] * num_spc_dates
    num_grid_rows = len(grid_point_lat)
    num_grid_columns = len(grid_point_long)
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
        multiday_storm_object_table = multiday_storm_object_table[multiday_storm_object_table['age_sec']>= 900]
        multiday_storm_object_table= multiday_storm_object_table.reset_index()
        del multiday_storm_object_table['index']

        print('total storm objects', len(multiday_storm_object_table))

        multi_storm_ids, place_holder = numpy.unique(multiday_storm_object_table['storm_id'].values, 
                                                     return_index = True)
        print('sift 1',len(place_holder))

        unique_times = [multiday_storm_object_table.loc[x]['unix_time_sec'] for x in place_holder]
        address_of_interest = []
        for x in place_holder:
            if ((max(multiday_storm_object_table['unix_time_sec']) - 86800)<= 
                multiday_storm_object_table.loc[x]['unix_time_sec']
                <= max(multiday_storm_object_table['unix_time_sec'])):
                address_of_interest.append(x)
        table_of_interest = []
        for x in address_of_interest:
            table_of_interest.append(multiday_storm_object_table.loc[x])
        centroids = get_the_centroid(multiday_storm_object_table['polygon_object_latlng'], address_of_interest)

        print('Number of births:',len(centroids))

        for i in range(0,len(grid_point_lat)):
            for j in range(0,len(grid_point_long)):
                count = 0 
                for k in range(0,len(centroids)):
                    # Find edges of grid cell (i, j).
                    this_cell_min_latitude_deg = (grid_point_lat[i] - (LATITUDE_SPACING_DEG/2))
                    this_cell_max_latitude_deg = (grid_point_lat[i] + (LATITUDE_SPACING_DEG/2))
                    
                    if this_cell_min_latitude_deg <= centroids[k,1] <=this_cell_max_latitude_deg:
                        this_cell_min_longitude_deg = (grid_point_long[j] - (LONGITUDE_SPACING_DEG/2))
                        this_cell_max_longitude_deg = (grid_point_long[j] + (LONGITUDE_SPACING_DEG/2)) 
                        
                        if this_cell_min_longitude_deg <= centroids[k,0] <= this_cell_max_longitude_deg:
                            count = count +1
                grid_cell_count_matrix[i,j] = grid_cell_count_matrix[i,j] + count
    grid_cell_count_matrix = numpy.ma.masked_where(grid_cell_count_matrix ==0, grid_cell_count_matrix)


m = Basemap(llcrnrlon=MIN_LONG_DEG, llcrnrlat=MIN_LAT_DEG, 
            urcrnrlon=(MIN_LONG_DEG +(NUM_COLUMNS*LONGITUDE_SPACING_DEG -1)), urcrnrlat=(MIN_LAT_DEG + (NUM_ROWS*LATITUDE_SPACING_DEG -1)))
x, y = m(lons,lats)
m.drawstates()
m.drawcountries()
m.drawcoastlines()
m.contourf(x,y, grid_cell_count_matrix)
m.colorbar()
plt.title('Storm Birth Frequency April 2011')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.show()
