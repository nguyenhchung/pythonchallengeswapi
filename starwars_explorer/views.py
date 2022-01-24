from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core import serializers
from django.template import loader
from django.template.defaulttags import csrf_token
from django.views import generic, View
from django.utils import timezone
from .models import Collection
from helpers import utils
from helpers.constants import DEFAULT_LIMIT, DEFAULT_OFFSET, SWAPI_CSV_HEADER_FIELDS
from .errors import EmptyCollection

def index(request):    
    collection_list = Collection.objects.order_by('-date')
    template = loader.get_template('starwars_explorer/index.html')
    context = {
        'collection_list': collection_list
    }
    return HttpResponse(template.render(context, request))
 
def fetch_data(request):
    # ajax request with POST method
    if request.is_ajax and request.method == "POST":
        
        # fetch logic        
        try:
            fetched_collection = utils.fetch_swapi()
            response_json = collection_to_json_response(fetch_collection)
            return JsonResponse(response_json, status=200)
        except Exception as e:
            return JsonResponse({"error": e}, status=400)

    return JsonResponse({"error": "Unknown error"}, status=500)

    
def collection_view(request, collection_id):
    try:
        result_limit = int(request.GET.get('limit', DEFAULT_LIMIT))
        collection = Collection.objects.get(pk=collection_id)
        file_content = utils.reading_csv_file(collection.filename)[:result_limit]
        
        if not(file_content and len(file_content) > 0):
            raise EmptyCollection
        
        next_limit = result_limit + DEFAULT_OFFSET
        load_more_is_disabled = True if result_limit >= collection.total_count else False  
    except Collection.DoesNotExist:
        raise Http404("Collection does not exist")
    except EmptyCollection:
        raise Http404("Empty collection")
    
    return render(request, 'starwars_explorer/collection_view.html', {'collection': collection, 'header_fields': SWAPI_CSV_HEADER_FIELDS, 'file_content': file_content, 'next_limit': str(next_limit), 'load_more_is_disabled': load_more_is_disabled})


def collection_count_view(request, collection_id):
    try:        
        count_fields = request.GET.get('fields').split(',')
        is_last_count_field = False if len(count_fields) > 1 else True
        
        collection = Collection.objects.get(pk=collection_id)
        count_dict = utils.retrieve_collection_count_dict(collection, count_fields)
           
        advanced_header_fields = utils.generate_advanced_swapi_header_fields(count_fields) 
    except Collection.DoesNotExist:
        raise Http404("Collection does not exist")
    return render(request, 'starwars_explorer/collection_count_view.html', {'collection': collection, 'advanced_header_fields': advanced_header_fields, 'count_fields': count_fields, 'count_dict':count_dict, 'is_last_count_field':is_last_count_field})