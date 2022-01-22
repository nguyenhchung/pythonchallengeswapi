import uuid
import requests
import csv
import time 
import datetime
from starwars_explorer.models import Collection
from starwars_explorer.SWAPIHandler import SWAPIPeopleEndpoint
from helpers.constants import *
from django.utils import timezone
from django.utils.dateformat import DateFormat
import pandas as pd


# helper functions

def iso8601_str_to_date(input_str):
    return datetime.datetime.strptime(input_str, ISO8601_FORMAT).strftime(EXPECTED_DATE_FORMAT)

def dt_to_django_template_dt(input_dt):
    return DateFormat(input_dt).format('N j, Y, P')
    

# fetch relevant functions

def retrieve_homeworld(input_url):
    # todo: include in SWAPIhandler and enable direct url inputs
    return requests.get(input_url).json()['name']
    
def transform_homeworld_field(homeworld_url, homeworld_dict={}):
    # retrieve homeworld from local dict to avoid multiple same api calls
    if homeworld_url not in homeworld_dict:
        homeworld_dict[homeworld_url] = retrieve_homeworld(homeworld_url)
    return homeworld_dict[homeworld_url]
    
def transform_swapi_row(input_row, homeworld_dict={}):
    transformed_row = input_row
    transformed_row['date'] = iso8601_str_to_date(input_row['edited'])
    transformed_row['homeworld'] = transform_homeworld_field(input_row['homeworld'], homeworld_dict)
        
    for key_to_drop in swapi_keys_to_drop:
        transformed_row.pop(key_to_drop)
    
    return transformed_row
    
def transform_swapi_results(input_list):
    homeworld_dict = {}
    transformed_list = []
     
    for input_row in input_list:
        transformed_row = transform_swapi_row(input_row, homeworld_dict)
        transformed_list.append(transformed_row)
    return transformed_list

def get_keys_from_dict(input_dict):
    return list(input_dict.keys())

def write_list_to_csv_file(input_list, filename):
    if input_list and len(input_list) > 0:
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = get_keys_from_dict(input_list[0])
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for input_row in input_list:
                writer.writerow(input_row)


def generate_file_name():
    return str(uuid.uuid4()) + '.csv'

def save_collection(file_name, total_count):
    new_collection = Collection(filename = file_name,
                                date=timezone.now(),
                                total_count=total_count)
    new_collection.save()
    return new_collection
    
def fetch_transformed_swapi_list():
    total_count, swapi_results = SWAPIPeopleEndpoint().get_total_list()
    transformed_list = transform_swapi_results(swapi_results)
    return total_count, transformed_list

def fetch_swapi():
    total_count, transformed_list = fetch_transformed_swapi_list()
    
    file_name = generate_file_name()
    
    write_list_to_csv_file(transformed_list, file_name)
    
    new_collection = save_collection(file_name, total_count)
    
    return new_collection


# file reading relevant functions

def reading_csv_file(filename):
    # this part can get upgraded with pandas or any other large data framework
    data_list = []
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        data_list = [ row for row in reader ]
    return data_list


# count relevant functions

def generate_advanced_header_fields(header_fields, selected_fields):
    advanced_header_fields = []
    
    for header_field in header_fields:
        targets = selected_fields.copy()
        selected = False
        disabled = False    
        if header_field in selected_fields:
            targets.remove(header_field)
            selected = True
            
            # disable of deselecting last field
            if len(selected_fields) == 1:
                disabled = True 
        else:
            targets.append(header_field)
        
        target_str = ','.join(filter(lambda x: x != "", targets))
        
        advanced_header_fields.append({'name': header_field, 'targets': target_str, 'selected': selected, 'disabled': disabled })
        
    return advanced_header_fields

def convert_csv_to_df(filename):
    return pd.read_csv(filename, engine='python')
    
def get_collection_count(df, count_fields):
    return df.groupby(count_fields).size()