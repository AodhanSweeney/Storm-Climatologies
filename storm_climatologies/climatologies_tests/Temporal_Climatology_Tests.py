"""Unit testing for Getting Dates Needed Climatology"""
import unittest
import numpy  # You forgot to import numpy.

working_date_index = 3
num_dates = 7
BIRTH_DAYS = [2,3]
DEATH_DAYS = [3,4]
PASSAGE_DAYS = [3]

# You forgot to define these variables somewhere in the file with unit tests.  However, the best practice would be to create a file (called "temporal_binning.py" or something) with constants BIRTH_CLIMATOLOGY_TYPE, DEATH_CLIMATOLOGY_TYPE, and PASSAGE_CLIMATOLOGY_TYPE defined at the top.  Then, when referencing those constants from outside the file, you would type "temporal_binning.BIRTH_CLIMATOLOGY_TYPE".
BIRTH_CLIMATOLOGY_TYPE = 'birth'
DEATH_CLIMATOLOGY_TYPE = 'death'
PASSAGE_CLIMATOLOGY_TYPE = 'passage'

# ClassNamesShouldAllBeFormattedLikeThis, with no underscores and a capital letter at the beginning of each word.  That's why your code didn't run the first time.
class CorrectDateRetrievalTests(unittest.TestCase):
    """Each method is a unit test for (Temporal/Spatial) (Birth/Death/passage) Climatology.py."""
    
    # method_names_should_be_defined_like_this, with no capital letters.
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


storm_id_and_hour_string = ['0001_9','2012_04']
time = numpy.array([9,4])

class CorrectHourStringParsingTest(unittest.TestCase):
    """Obtaining the correct hour string """
    
    def test_get_hour_integer(self):
        """ensures correct output for parsing of hour string"""
        correct_hour_time = _parse_storm_id_and_hour_strings(storm_id_and_hour_string)
        
        self.assertTrue(numpy.allclose(correct_hour_time, time))

        
if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)