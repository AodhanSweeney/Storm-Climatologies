def get_the_centroid(shapely_point_list_of_centroids):
    """turns the shapely point list taken from the multiday storm object table
    and converts it into a numpy array of the centroids"""

    centroids = []
    for iterator in shapely_point_list_of_centroids:
        centroid_pt = iterator.centroid
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


import unittest
import numpy
from gewittergefahr.gg_utils import error_checking
from gewittergefahr.gg_utils import longitude_conversion as lng_conversion
from shapely.geometry import Polygon

SHAPELY_POINT_LIST_OF_CENTROIDS = [Polygon([(0,0),(2,2),(0,2),(2,0)]), Polygon([(0,0), (1,5), (2,0)])]

CENTROIDS_WANTED= numpy.array([(1.,1.),(1., 1.666666666666667)])

"""global variables defined for creating a made up grid that spans from lat=5 lng=5 to lat=15 lng=15 
with 1 deg spacing"""

MIN_LAT_DEG = 5.0

MIN_LNG_DEG = 5.0

LAT_SPACING_DEG = 1.0

LNG_SPACING_DEG =1.0

NUM_ROWS = 10

NUM_COLUMNS = 10

GRID_POINT_LATS_WANTED = numpy.array([ 5.,  6.,  7.,  8.,  9., 10., 11., 12., 13., 14.])

GRID_POINT_LNGS_WANTED = numpy.array([ 5.,  6.,  7.,  8.,  9., 10., 11., 12., 13., 14.])

GRID_ARRAY_WANTED = [GRID_POINT_LATS_WANTED, GRID_POINT_LNGS_WANTED]

LAT_LNG_MATRICES = [[[ 5.,  5.,  5.,  5.,  5.,  5.,  5.,  5.,  5.,  5.],
       [ 6.,  6.,  6.,  6.,  6.,  6.,  6.,  6.,  6.,  6.],
       [ 7.,  7.,  7.,  7.,  7.,  7.,  7.,  7.,  7.,  7.],
       [ 8.,  8.,  8.,  8.,  8.,  8.,  8.,  8.,  8.,  8.],
       [ 9.,  9.,  9.,  9.,  9.,  9.,  9.,  9.,  9.,  9.],
       [10., 10., 10., 10., 10., 10., 10., 10., 10., 10.],
       [11., 11., 11., 11., 11., 11., 11., 11., 11., 11.],
       [12., 12., 12., 12., 12., 12., 12., 12., 12., 12.],
       [13., 13., 13., 13., 13., 13., 13., 13., 13., 13.],
       [14., 14., 14., 14., 14., 14., 14., 14., 14., 14.]], 
                    [[ 5.,  6.,  7.,  8.,  9., 10., 11., 12., 13., 14.],
       [ 5.,  6.,  7.,  8.,  9., 10., 11., 12., 13., 14.],
       [ 5.,  6.,  7.,  8.,  9., 10., 11., 12., 13., 14.],
       [ 5.,  6.,  7.,  8.,  9., 10., 11., 12., 13., 14.],
       [ 5.,  6.,  7.,  8.,  9., 10., 11., 12., 13., 14.],
       [ 5.,  6.,  7.,  8.,  9., 10., 11., 12., 13., 14.],
       [ 5.,  6.,  7.,  8.,  9., 10., 11., 12., 13., 14.],
       [ 5.,  6.,  7.,  8.,  9., 10., 11., 12., 13., 14.],
       [ 5.,  6.,  7.,  8.,  9., 10., 11., 12., 13., 14.],
       [ 5.,  6.,  7.,  8.,  9., 10., 11., 12., 13., 14.]]]


class ErrorCheckingTests(unittest.TestCase):
    """assertion that functions are working correclty"""
    
    
    def test_get_centroid(self):
        """ensures correct output for shapely points from the get_the_centroid function. """
        centroids_gotten = get_the_centroid(SHAPELY_POINT_LIST_OF_CENTROIDS)
        
        self.assertTrue(numpy.allclose(centroids_gotten, CENTROIDS_WANTED))
    
    
    
    def test_latlng_grid_points(self):
        """ensures correct output for greating two numpy arrays of the required grid lat/long points"""
        grids_gotten = get_latlng_grid_points(min_latitude_deg=MIN_LAT_DEG, min_longitude_deg=MIN_LNG_DEG,
                           lat_spacing_deg=LAT_SPACING_DEG, lng_spacing_deg=LNG_SPACING_DEG,
                           num_rows=NUM_ROWS, num_columns=NUM_COLUMNS)
    
        self.assertTrue(numpy.allclose(grids_gotten, GRID_ARRAY_WANTED))
        
    
    
    def test_latlng_vectors_to_matrices(self):
        """ensures correct output for turning the numpy arrays retrieved in get_latlng_grid_points into 
        matricies that are used for the spatial mapping"""
        matrix_gotten = latlng_vectors_to_matrices(GRID_POINT_LATS_WANTED,GRID_POINT_LNGS_WANTED)
    
        self.assertTrue(numpy.allclose(matrix_gotten, LAT_LNG_MATRICES))


    
if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)