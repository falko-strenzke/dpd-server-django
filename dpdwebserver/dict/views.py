from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, HttpRequest
from django.views.generic import ListView
#from django.db.models.query import QuerySet
from .models import Inflected_Form
from .models import Headword
import os
import markdown


def render_markdown_file(request : HttpRequest):
    """
    render a page from a markdown file. The markdown file is determined by the last element of the URL.
    """
    req_path = request.get_full_path()
    if req_path[-1] == "/":
        req_path = req_path[:-1]
    base_name = os.path.basename(req_path)
    module_dir = os.path.dirname(__file__)
    file_path = os.path.join(module_dir, f"content/md/{base_name}.md")
    data_file = open(file_path, 'r')
    data = data_file.read()
    context = {
        'content': markdown.markdown(data, extensions=['tables']),
    }
    return render(request, 'md_content.html', context)


class SearchEntriesOfDictView(ListView):
    """Search view for the entries of a specific dictionary"""
    #from https://learndjango.com/tutorials/django-search-tutorial
    # as an alternative function-based view check out
    # https://linuxhint.com/build-a-basic-search-for-a-django/
    model = Inflected_Form
    template_name = "search_entries_of_dict.html"

    def get_context_data(self, **kwargs):

        query = self.request.GET.get("q")
        context = super(ListView, self).get_context_data(**kwargs)
        context['query_string_with_label'] = "search query: " + query + "\n" if query not in [None, ''] else ''
        context['query_string'] = query if query not in [None, ''] else ''
        search_type = self.request.GET.get("search_type")
        if search_type == "":
            search_type = "exact"
        context['search_type'] = search_type


        return context

    def get_queryset(self): # new
        query = self.request.GET.get("q")
        search_type = self.request.GET.get("search_type")
        print(search_type)
        limit_headwords = 400
        limit_inflected = 400
        if query is not None:
            result : list[str] = []
            if search_type == 'exact':
                result = [h.headword for h in list(Headword.objects.filter(headword__iexact=query).order_by("headword")[:limit_headwords])]
                result += list(set([w.inflected_form for w in list(Inflected_Form.objects.filter(inflected_form__iexact=query).order_by("inflected_form")[:limit_inflected])]))
            elif search_type == 'substring_match':
                result = [h.headword for h in list(Headword.objects.filter(headword__icontains=query).order_by("headword")[:limit_headwords])]
                result +=  list(set([w.inflected_form for w in list(Inflected_Form.objects.filter(inflected_form__icontains=query).order_by("inflected_form")[:limit_inflected])]))
            elif search_type == 'starts_with':
                result = [h.headword for h in list(Headword.objects.filter(headword__istartswith=query).order_by("headword")[:limit_headwords])]
                result +=  list(set([w.inflected_form for w in list(Inflected_Form.objects.filter(inflected_form__istartswith=query).order_by("inflected_form")[:limit_inflected])]))
            elif search_type == 'ends_with':
                result = [h.headword for h in list(Headword.objects.filter(headword__iendswith=query).order_by("headword")[:limit_headwords])]
                result += list(set([w.inflected_form for w in list(Inflected_Form.objects.filter(inflected_form__iendswith=query).order_by("inflected_form")[:limit_inflected])]))
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
