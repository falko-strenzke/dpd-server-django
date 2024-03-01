import os
from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, HttpRequest
from django.views.generic import ListView
import markdown
#from django.db.models.query import QuerySet
from .models import Inflected_Form, Headword, Deconstruction, Grammar, Construction_Element, Construction_Element_Set


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
    data_file = open(file_path, 'r', encoding="utf-8")
    data = data_file.read()
    context = {
        'content': markdown.markdown(data, extensions=['tables']),
    }
    return render(request, 'md_content.html', context)


class SearchByConsructionView(ListView):
    """Search view for the entries of a specific dictionary"""
    #from https://learndjango.com/tutorials/django-search-tutorial
    # as an alternative function-based view check out
    # https://linuxhint.com/build-a-basic-search-for-a-django/
    model = Inflected_Form
    template_name = "search_construction.html"

    def get_context_data(self, **kwargs):

        query = self.request.GET.get("q")
        context = super(ListView, self).get_context_data(**kwargs)
        context['query_string_with_label'] = "search query: " + query + "\n" if query not in [None, ''] else ''
        context['query_string'] = query if query not in [None, ''] else ''
        search_type = self.request.GET.get("search_type")
        if search_type == "":
            search_type = "exact"
        context['autocomplete_list'] = [x.text for x in list(Construction_Element_Set.objects.all())]
        return context

    def search_headwords_by_construction(self) -> list[str]:
        class HeadwordInfo:
            def __init__(self, headword_link, construction_text):
                self.headword_link = headword_link
                self.construction_text = construction_text
        limit = 1000
        # TODO: filter out queries where whitespace or other invalid chars is enclosed by separator char(s)
        query = self.request.GET.get("q")
        # parse the query into tokens separated by "+"
        query = query.strip() # strip of leading or trailing spaces
        query = query.strip(",")
        query_plus_sep_toks = query.split(',')
        print("query_plus_sep_toks = " + str(query_plus_sep_toks))
        query_plus_sep_toks = [x.strip() for x in query_plus_sep_toks]
        if len(query_plus_sep_toks) == 0:
            return []
        search = Headword.objects.filter(construction_element__text__iexact=query_plus_sep_toks[0])
        query_plus_sep_toks = query_plus_sep_toks[1:]
        # Blog.objects.filter(entry__headline__contains="Lennon")
        result : list[HeadwordInfo] = []
        for query_tok in query_plus_sep_toks:
            search = search.filter(construction_element__text__iexact=query_tok)
        result_set_headwords = {w.headword for w in list(search)[:limit]}
        for hw in result_set_headwords:
            print("appending result for headword: '" + hw + "'")
            result.append(HeadwordInfo(hw, Headword.objects.get(headword=hw).construction_text))
        return result


    def get_queryset(self): # new
        query = self.request.GET.get("q")
        search_type = self.request.GET.get("search_type")
        print(search_type)
        if query is not None:
            return self.search_headwords_by_construction()
        return []


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
        query : str = self.request.GET.get("q")
        search_type = self.request.GET.get("search_type")
        limit_headwords = 300
        limit_inflected = 300
        limit_deconstruction = 300
        limit_grammar = 300
        set_of_search_results : set[str] = set()
        if query is not None:
            query = query.strip()
            result : list[str] = []
            if search_type == 'exact':
                # TODO: SENSELESS SET COMPREHENSION (?):
                [set_of_search_results.add(h.headword) for h in list(Headword.objects.filter(headword__iexact=query).order_by("headword")[:limit_headwords])]
                set_of_search_results.update(set([w.inflected_form for w in list(Inflected_Form.objects.filter(inflected_form__iexact=query).order_by("inflected_form")[:limit_inflected])]))
                set_of_search_results.update(set([w.headword for w in list(Deconstruction.objects.filter(headword__iexact=query).order_by("headword")[:limit_deconstruction])]))
                set_of_search_results.update(set([w.headword for w in list(Grammar.objects.filter(headword__iexact=query).order_by("headword")[:limit_grammar])]))
            elif search_type == 'substring_match':
                [set_of_search_results.add(h.headword) for h in list(Headword.objects.filter(headword__icontains=query).order_by("headword")[:limit_headwords])]
                set_of_search_results.update(set([w.inflected_form for w in list(Inflected_Form.objects.filter(inflected_form__icontains=query).order_by("inflected_form")[:limit_inflected])]))
                set_of_search_results.update(set([w.headword for w in list(Deconstruction.objects.filter(headword__icontains=query).order_by("headword")[:limit_deconstruction])]))
                set_of_search_results.update(set([w.headword for w in list(Grammar.objects.filter(headword__icontains=query).order_by("headword")[:limit_grammar])]))
            elif search_type == 'starts_with':
                [set_of_search_results.add(h.headword) for h in list(Headword.objects.filter(headword__istartswith=query).order_by("headword")[:limit_headwords])]
                set_of_search_results.update(set([w.inflected_form for w in list(Inflected_Form.objects.filter(inflected_form__istartswith=query).order_by("inflected_form")[:limit_inflected])]))
                set_of_search_results.update(set([w.headword for w in list(Deconstruction.objects.filter(headword__istartswith=query).order_by("headword")[:limit_deconstruction])]))
                set_of_search_results.update(set([w.headword for w in list(Grammar.objects.filter(headword__istartswith=query).order_by("headword")[:limit_grammar])]))
            elif search_type == 'ends_with':
                [set_of_search_results.add(h.headword) for h in list(Headword.objects.filter(headword__iendswith=query).order_by("headword")[:limit_headwords])]
                set_of_search_results.update(set([w.inflected_form for w in list(Inflected_Form.objects.filter(inflected_form__iendswith=query).order_by("inflected_form")[:limit_inflected])]))
                set_of_search_results.update(set([w.headword for w in list(Deconstruction.objects.filter(headword__iendswith=query).order_by("headword")[:limit_deconstruction])]))
                set_of_search_results.update(set([w.headword for w in list(Grammar.objects.filter(headword__iendswith=query).order_by("headword")[:limit_grammar])]))
            result = list(set_of_search_results)
            return result
        return []




def collect_headword_entries_descrs_from_table_headwords(headword : str = "") -> str:
    result = ""
    try:
        hw : Headword = Headword.objects.get(pk=headword)
    except Headword.DoesNotExist:
        hw = None
    if hw:
        result += hw.desc_html
    return result


def collect_headword_entries_descrs_from_supplementary_tables(key_for_supplementary_tables : str = "") -> str:
    result = ""
    try:
        gram : Grammar = Grammar.objects.get(pk=key_for_supplementary_tables)
    except Grammar.DoesNotExist:
        gram = None
    if gram:
        result += gram.desc_html
    try:
        dec : Deconstruction = Deconstruction.objects.get(pk=key_for_supplementary_tables)
    except Deconstruction.DoesNotExist:
        dec = None
    if dec:
        result += dec.desc_html
    return result


def lookup_word(request : HttpRequest, word : str):
    """Lookup a word in the dictionary dictionary"""
    #print(request.get_full_path())
    template = "lookup_word.html"
    if request.get_full_path().startswith('/dict/dpd/lookup_gd/word/'):
        template = "lookup_word_gd.html"
    word = word.replace("ṁ", "ṃ")
    inflected_forms : list[Inflected_Form] = list(Inflected_Form.objects.filter(inflected_form=word))
    result = ""
    if len(inflected_forms) > 0:
        for inflected_form in inflected_forms:
            hw : Headword = Headword.objects.get(pk=inflected_form.link_text)
            result += hw.desc_html
    else:
        print("collecting from word directly")
        result += collect_headword_entries_descrs_from_table_headwords(word)
    result += collect_headword_entries_descrs_from_supplementary_tables(word)
    if result == "":
        response = HttpResponse()
        response.status_code = 404
        return response

    context = {
        'body': result,
    }
    return render(request, template, context)
