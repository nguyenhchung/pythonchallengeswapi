from django.test import TestCase
from helpers.unittest import *
from helpers import utils
# Create your tests here.


class SWAPITestCase(TestCase):
    
    def test_transform_swapi_results(self):
        test_list = SWAPI_RESPONSE_EXAMPLE
        transformed_list = utils.transform_swapi_results(test_list)
        self.assertTrue(transformed_list, TRANSFORMED_EXAMPLE)
    
    def test_reading_csv_file(self):
        test_file = 'helpers/fetch-unittest.csv'
        csv_list = utils.reading_csv_file(test_file)
        self.assertTrue(csv_list, READ_CSV_EXAMPLE)
        
    def test_advanced_header_logic(self):
        selection = ['hair_color']
        advanced_header = utils.generate_advanced_swapi_header_fields(selection)  
        self.assertTrue(advanced_header, SELECT_HAIR_COLOR_EXAMPLE)
        selection.append('skin_color')
        advanced_header = utils.generate_advanced_swapi_header_fields(selection)
        self.assertTrue(advanced_header, SELECT_HAIR_COLOR_AND_SKIN_COLOR_EXAMPLE)
        selection.remove('hair_color')
        self.assertTrue(advanced_header, SELECT_SKIN_COLOR_EXAMPLE)
        
    def test_collection_count(self):
        test_file = 'helpers/fetch-unittest.csv'
        count_fields = ['gender','hair_color']
        count_dict = utils.retrieve_collection_count_dict(test_file, count_fields)
        self.assertTrue(count_dict, COUNT_DICT_EXAMPLE)