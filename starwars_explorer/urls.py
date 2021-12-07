from django.urls import path

from . import views

app_name = 'starwars_explorer'
urlpatterns = [
    path('', views.index, name = 'index'),#views.Index.as_view()),
    path('fetch/data', views.fetch_data, name = 'fetch_data'),
    path('<int:collection_id>/', views.collection_view, name='collection_view'),
    path('<int:collection_id>/count/', views.collection_count_view, name='collection_count_view')
]