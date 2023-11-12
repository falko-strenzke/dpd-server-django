from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, HttpRequest
from django.views.generic import ListView
#from django.db.models.query import QuerySet
from .models import Inflected_Form
from .models import Headword
import os
import markdown


def index(request):
    module_dir = os.path.dirname(__file__)
    file_path = os.path.join(module_dir, 'content/md/index.md')
    data_file = open(file_path, 'r')
    data = data_file.read()
    context = {
        'content': markdown.markdown(data),
    }
    return render(request, 'md_content.html', context)


class SearchEntriesOfDictView(ListView):
    """Search view for the entries of a specific dictionary"""
    #from https://learndjango.com/tutorials/django-search-tutorial
    # as an alternative function-based view check out
    # https://linuxhint.com/build-a-basic-search-for-a-django/
    model = Inflected_Form
    template_name = "search_entries_of_dict.html"



    #def get_context_data(self, **kwargs):
    #    query = self.request.GET.get("q")
    #    context = super(ListView, self).get_context_data(**kwargs)
    #    context['query_string_with_label'] = "search query: " + query + "\n" if query not in [None, ''] else ''
    #    return context


    def get_context_data(self, **kwargs):

        query = self.request.GET.get("q")
        context = super(ListView, self).get_context_data(**kwargs)
        context['query_string_with_label'] = "search query: " + query + "\n" if query not in [None, ''] else ''
        return context

    def get_queryset(self): # new
        query = self.request.GET.get("q")
        result = []
        limit_headwords = 400
        limit_inflected = 400
        if query is not None:
            result = Headword.objects.filter(headword__icontains=query).order_by("headword")[:limit_headwords]
            inflected_forms : list[Inflected_Form] = list(Inflected_Form.objects.filter(inflected_form__icontains=query).order_by("inflected_form")[:limit_inflected])
            for inflected_form in inflected_forms:
                result |= Headword.objects.filter(pk=inflected_form.link_text)
            #    result = QuerySet.union(result, result_hw)
            return result
        return []


def lookup_word(request : HttpRequest, word):
    """Lookup a word in the dictionary dictionary"""
    #print(request.get_full_path())
    template = "lookup_word.html"
    if request.get_full_path().startswith('/dict/dpd/lookup_gd/word/'):
        template = "lookup_word_gd.html"
    inflected_forms : list[Inflected_Form] = list(Inflected_Form.objects.filter(inflected_form=word))
    result = ""
    if len(inflected_forms) > 0:
        for inflected_form in inflected_forms:
            hw : Headword = Headword.objects.get(pk=inflected_form.link_text)
            result += hw.desc_html
    else:
        try:
            hw : Headword = Headword.objects.get(pk=word)
        except Headword.DoesNotExist:
            hw = None
        if hw:
            result += hw.desc_html
        else:
            response = HttpResponse()
            response.status_code = 404
            return response

    context = {
        'body': result,
    }
    return render(request, template, context)
    #return HttpResponse(result)
