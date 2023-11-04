from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("search/", views.SearchEntriesOfDictView.as_view(), name="search_entries_of_dict"),
]
