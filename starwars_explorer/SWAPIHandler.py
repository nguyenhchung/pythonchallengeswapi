from urllib.parse import urlparse
from urllib.parse import parse_qs
import requests

def extract_page_query_param(input_url, query_key):
    parsed_url = urlparse(input_url)
    return parse_qs(parsed_url.query)[query_key][0]


SWAPI_BASE_URL = 'https://swapi.dev/api/'

class SWAPIBaseEndpoint:
    endpoint_path = ''
    
    default_payload = {}
    
    def call_endpoint(self, payload=default_payload):
        
        api_url = SWAPI_BASE_URL + self.endpoint_path
        response = requests.get(api_url, params=payload)
        
        if response.status_code != 200:
            raise Exception("Unsuccessful API call")
        else:
            return response
        
    def get_total_list(self, payload=default_payload):
        total_list = []
        
        start_response = self.call_endpoint(payload=payload)
        start_response_json = start_response.json()
        
        total_count = start_response_json.get('count', None)
        start_response_items = start_response_json.get('results', [])
        total_list.extend(start_response_items)
        next_page_token = start_response_json.get('next', None)
        
        while(next_page_token):
            new_payload = payload
            next_page = extract_page_query_param(next_page_token, 'page')
            new_payload['page'] = next_page
            response = self.call_endpoint(payload=new_payload)
            response_items = response.json().get('results', [])
            total_list.extend(response_items)
            next_page_token = response.json().get('next', None)
            
        return total_count, total_list
        
class SWAPIPeopleEndpoint(SWAPIBaseEndpoint):
    endpoint_path = 'people/'