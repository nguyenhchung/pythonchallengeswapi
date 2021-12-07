from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core import serializers
from django.template import loader
from django.template.defaulttags import csrf_token
from django.views import generic, View
from django.utils import timezone
from .models import Collection
from helpers import utils
from helpers.constants import DEFAULT_LIMIT, DEFAULT_OFFSET

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
        is_valid = True
        errors = None
        
        instance = utils.fetch_swapi()
        
        date_formatted = utils.dt_to_django_template_dt(instance.date)
        response_json = {   "pk": instance.pk,
                            "instance": 
                            { 
                                "filename": instance.filename,
                                "date": date_formatted,
                                "total_count": instance.total_count 
                            }
                        }
        
        if is_valid:
            return JsonResponse(response_json, status=200)
        else:
            return JsonResponse({"error": errors}, status=400)

    return JsonResponse({"error": "Unknown error"}, status=400)

    
def collection_view(request, collection_id):
    try:
        result_limit = int(request.GET.get('limit', DEFAULT_LIMIT))
        collection = Collection.objects.get(pk=collection_id)
        file_content = utils.reading_csv_file(collection.filename)[:result_limit]
        next_limit = result_limit + DEFAULT_OFFSET
        load_more_disabled = True if result_limit >= collection.total_count else False  
        
        header_fields = []
        if file_content and len(file_content) > 0:
            header_fields = file_content[0].keys()
    except Collection.DoesNotExist:
        raise Http404("Collection does not exist")
    return render(request, 'starwars_explorer/collection_view.html', {'collection': collection, 'header_fields': header_fields, 'file_content': file_content, 'next_limit': str(next_limit), 'load_more_disabled': load_more_disabled})


def collection_count_view(request, collection_id):
    try:        
        count_fields = request.GET.get('fields').split(',')
        is_last_count_field = False if len(count_fields) > 1 else True
        
        collection = Collection.objects.get(pk=collection_id)
        
        file_content = utils.reading_csv_file(collection.filename)
        df = utils.convert_csv_to_df(collection.filename)
        count_dict = utils.get_collection_count(df, count_fields).to_dict()
        
        header_fields = []
        if file_content and len(file_content) > 0:
            header_fields = file_content[0].keys()    
        
        advanced_header_fields = utils.generate_advanced_header_fields(header_fields, count_fields) 
    except Collection.DoesNotExist:
        raise Http404("Collection does not exist")
    return render(request, 'starwars_explorer/collection_count_view.html', {'collection': collection, 'advanced_header_fields': advanced_header_fields, 'count_fields': count_fields, 'count_dict':count_dict, 'is_last_count_field':is_last_count_field})