"""Unit testing for Getting Dates Needed Climatology"""
import unittest
import numpy  
from gewittergefahr.gg_utils import error_checking
from gewittergefahr.gg_utils import longitude_conversion as lng_conversion
from shapely.geometry import Polygon

working_date_index = 3
num_dates = 7
BIRTH_DAYS = [2,3]
DEATH_DAYS = [3,4]
PASSAGE_DAYS = [3]

BIRTH_CLIMATOLOGY_TYPE = 'birth'
DEATH_CLIMATOLOGY_TYPE = 'death'
PASSAGE_CLIMATOLOGY_TYPE = 'passage'

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

STORM_ID_AND_HOUR_STRING = ['0001_9','2012_04']

TIME = numpy.array([9,4])

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

class CorrectDateRetrievalTests(unittest.TestCase):
    """Each method is a unit test for (Temporal/Spatial) (Birth/Death/passage) Climatology.py."""

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

    def test_get_dates_needed_birth(self):
        """ensures correct output for the dates in needed apendix"""
        these_dates_expected = _get_dates_needed(working_date_index, num_dates, BIRTH_CLIMATOLOGY_TYPE)

        self.assertTrue(numpy.allclose(these_dates_expected, BIRTH_DAYS))

    def test_get_dates_needed_death(self):
        these_dates_expected = _get_dates_needed(working_date_index, num_dates, DEATH_CLIMATOLOGY_TYPE)

        self.assertTrue(numpy.allclose(these_dates_expected, DEATH_DAYS))

    def test_get_dates_needed_passage(self):
        these_dates_expected = _get_dates_needed(working_date_index, num_dates, PASSAGE_CLIMATOLOGY_TYPE)

        self.assertTrue(numpy.allclose(these_dates_expected, PASSAGE_DAYS))

    def test_get_hour_integer(self):
        """ensures correct output for parsing of hour string"""
        correct_hour_time = _parse_storm_id_and_hour_strings(storm_id_and_hour_string)

            self.assertTrue(numpy.allclose(correct_hour_time, time))


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
