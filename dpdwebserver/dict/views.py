from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.views.generic import ListView
#from django.db.models.query import QuerySet
from .models import Inflected_Form
from .models import Headword


def index(request):
    return HttpResponse("Hello, world. You're at the DPD index.")


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
        if query is not None:
            result = Headword.objects.filter(headword__icontains=query)
            inflected_forms : list[Inflected_Form] = list(Inflected_Form.objects.filter(inflected_form__icontains=query))
            for inflected_form in inflected_forms:
                result |= Headword.objects.filter(pk=inflected_form.link_text)
            #    result = QuerySet.union(result, result_hw)
            return result
        return Headword.objects.filter()


def lookup_word(request, word):
    """Lookup a word in the dictionary dictionary"""
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
            result = "word not found"

    context = {
        'body': result,
    }
    return render(request, 'lookup_word.html', context)
    #return HttpResponse(result)
