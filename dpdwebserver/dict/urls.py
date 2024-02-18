from django.urls import path

from . import views

urlpatterns = [
    # for markdown files under the dict/content/md, the first argument must amount to the file name under the folder "md".
    path("dpd/", views.render_markdown_file, name="dpd_page"),
    path("velthuis/", views.render_markdown_file, name="velthuis_page"),
    path("construction_search/", views.render_markdown_file, name="construction_search_instructions_page"),
    path("dpd/search/", views.SearchEntriesOfDictView.as_view(), name="search_entries_of_dict"),
    path("dpd/search_construction/", views.SearchByConsructionView.as_view(), name="search_by_construction"),
    path("dpd/lookup/<str:word>", views.lookup_word, name="lookup_word"),
    path("dpd/lookup_gd/word/<str:word>", views.lookup_word, name="lookup_word_gd"),
]
