from django.urls import path

from . import views

urlpatterns = [
    path("dpd/", views.render_markdown_file, name="dpd_page"),
    path("velthuis/", views.render_markdown_file, name="velthuis_page"),
    path("dpd/search/", views.SearchEntriesOfDictView.as_view(), name="search_entries_of_dict"),
    path("dpd/lookup/word/<str:word>", views.lookup_word, name="lookup_word"),
    path("dpd/lookup_gd/word/<str:word>", views.lookup_word, name="lookup_word_gd"),
]
