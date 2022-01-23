from urllib.parse import urlparse
from urllib.parse import parse_qs
import requests

def extract_page_query_param(input_url, query_key):
    parsed_url = urlparse(input_url)
    return parse_qs(parsed_url.query)[query_key][0]


SWAPI_BASE_URL = 'https://swapi.dev/api/'

class SWAPIResponse:
    # processing SWAPI specific responses
    
    total_list = []
    total_count = None
    next_page_token = None
    
    def __init__(self, start_response):
        self.add(start_response)
        
    def add(self, api_response):
        self.total_count = api_response.get('count', None)
        self.total_list.extend(api_response.get('results', []))
        self.next_page_token = api_response.get('next', None)


class SWAPIBaseEndpoint:
    endpoint_path = ''
    
    default_payload = {}
    
    def call_endpoint(self, payload=default_payload):
        api_url = SWAPI_BASE_URL + self.endpoint_path
        response = requests.get(api_url, params=payload)
        if response.status_code != 200:
            raise Exception("Unsuccessful API call")
        
        return response
 
        
    def get_total_list(self, payload=default_payload):
        total_list = []
        
        swapi_response = SWAPIResponse(self.call_endpoint(payload=payload).json())
        
        while(swapi_response.next_page_token):
            new_payload = payload
            new_payload['page'] = extract_page_query_param(swapi_response.next_page_token, 'page')
            
            swapi_response.add(self.call_endpoint(payload=new_payload).json())

        return swapi_response.total_count, swapi_response.total_list
        
class SWAPIPeopleEndpoint(SWAPIBaseEndpoint):
    endpoint_path = 'people/'