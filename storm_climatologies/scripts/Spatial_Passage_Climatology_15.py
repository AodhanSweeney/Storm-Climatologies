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
LAST_SPC_DATE_STRING = '20110410'
TOP_PROCESSED_DIR_NAME = '/Users/reu/Downloads/'
TRACKING_SCALE_METRES2 = 314159265
Sep_String = '*'*50

BIRTH_CLIMATOLOGY_TYPE = 'birth'
DEATH_CLIMATOLOGY_TYPE = 'death'
PASSAGE_CLIMATOLOGY_TYPE = 'passage'

MIN_LAT_DEG = 20.
MIN_LONG_DEG = 230.
LATITUDE_SPACING_DEG = 1.0 
LONGITUDE_SPACING_DEG = 1.0
NUM_ROWS = 35
NUM_COLUMNS = 60

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
    lats, lons = utils.latlng_vectors_to_matrices(grid_point_lat, grid_point_long)
    num_grid_rows = len(grid_point_lat)
    num_grid_columns = len(grid_point_long)
    grid_cell_count_matrix = numpy.full((num_grid_rows, num_grid_columns), 0, dtype=int)
    
    for working_date_index in range(num_spc_dates):
        multiday_storm_object_table = get_storm_object_table(num_spc_dates, Passage_Climatology, working_date_index)
        multiday_storm_object_table = multiday_storm_object_table[multiday_storm_object_table['age_sec']>= 900]
        
        
        centroids = get_the_centroid(multiday_storm_object_table['polygon_object_latlng'])
        print('Total number of Storm Objects:',len(centroids))

        for i in range(0,len(grid_point_lat)):
            for j in range(0,len(grid_point_long)):
                count = 0 
                for k in range(0,len(centroids)):
                    #print('grid row loop')
                    # Find edges of grid cell (i, j).
                    this_cell_min_latitude_deg = (grid_point_lat[i] - (LATITUDE_SPACING_DEG/2))
                    this_cell_max_latitude_deg = (grid_point_lat[i] + (LATITUDE_SPACING_DEG/2))
                    
                    if this_cell_min_latitude_deg <= centroids[k,1] <=this_cell_max_latitude_deg:
                        this_cell_min_longitude_deg = (grid_point_long[j] - (LONGITUDE_SPACING_DEG/2))
                        this_cell_max_longitude_deg = (grid_point_long[j] + (LONGITUDE_SPACING_DEG/2)) 
                        
                        if this_cell_min_longitude_deg <= centroids[k,0] <= this_cell_max_longitude_deg:
                            count = count +1
                grid_cell_count_matrix[i,j] = grid_cell_count_matrix[i,j] + count
    grid_cell_count_matrix = numpy.ma.masked_where(grid_cell_count_matrix == 0, grid_cell_count_matrix)
    
  m = Basemap(llcrnrlon=MIN_LONG_DEG, llcrnrlat=MIN_LAT_DEG, 
              urcrnrlon=(MIN_LONG_DEG + NUM_COLUMNS-1), urcrnrlat=(MIN_LAT_DEG + NUM_ROWS-1))
  x, y = m(lons,lats)
  m.drawstates()
  m.drawcountries()
  m.drawcoastlines()
  m.contourf(x,y, grid_cell_count_matrix)
  m.colorbar()
  plt.title('Relative Storm Frequency April 2011')
  plt.xlabel('Longitude')
  plt.ylabel('Latitude')
  plt.show()    
