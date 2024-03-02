import os
from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, HttpRequest
from django.views.generic import ListView
import markdown
#from django.db.models.query import QuerySet
from .models import Pali_Word, Pali_Root, Inflection_To_Headwords, Sandhi, Construction_Element, Construction_Element_Set


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
    #model = Inflected_Form
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
        search = Pali_Word.objects.filter(construction_element__text__iexact=query_plus_sep_toks[0])
        query_plus_sep_toks = query_plus_sep_toks[1:]
        # Blog.objects.filter(entry__headline__contains="Lennon")
        result : list[HeadwordInfo] = []
        for query_tok in query_plus_sep_toks:
            search = search.filter(construction_element__text__iexact=query_tok)
        result_set_headwords = {w.pali_1 for w in list(search)[:limit]}
        for hw in result_set_headwords:
            print("appending result for headword: '" + hw + "'")
            result.append(HeadwordInfo(hw, Pali_Word.objects.get(pali_1=hw).construction))
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
    #model = Inflected_Form
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


    def search_tables_generically(self, query : str, match_suffix_wo__ : str, set_of_search_results : set[str]) -> list[str]:

        limit_headwords = 300
        limit_inflected = 300
        limit_sandhi = 300
        #limit_grammar = 300

        # get the matching headwords
        [set_of_search_results.add(h.pali_1) for h in list(Pali_Word.objects.filter(**{f'pali_2__{match_suffix_wo__}': query}).order_by("pali_1")[:limit_headwords])]

        # get all the headwords to the inflected forms that match the query
        # TODO: BETTER LIST THE INFLECTED FORM AND ITS GRAM. INSTANCE
        #hw_list_from_inflected : list[str] = []
        #[hw_list_from_inflected.extend(h.headwords.split(",")) for h in list(Inflection_To_Headwords.objects.filter(**{f'inflection__{match_suffix_wo__}': query}).order_by("inflection")[:limit_inflected])]
        #hw_list_from_inflected = [x.strip() for x in hw_list_from_inflected]
        [set_of_search_results.add(h.inflection) for h in list(Inflection_To_Headwords.objects.filter(**{f'inflection__{match_suffix_wo__}': query}).order_by("inflection")[:limit_inflected])]

        # get the sandhi matches
        [set_of_search_results.add(h.sandhi) for h in list(Sandhi.objects.filter(**{f'sandhi__{match_suffix_wo__}': query}).order_by("sandhi")[:limit_sandhi])]


    def get_queryset(self): # new
        query : str = self.request.GET.get("q")
        search_type = self.request.GET.get("search_type")
        set_of_search_results : set[str] = set()
        if query is not None:
            query = query.strip()
            result : list[str] = []
            match_suffix_wo__ : str = ""
            if search_type == 'exact':
                match_suffix_wo__ = "iexact"
                # TODO: ADD Sandhi
                #[set_of_search_results.add(h.pali_1) for h in list(Pali_Word.objects.filter(pali_2__iexact=query).order_by("pali_1")[:limit_headwords])]
                #set_of_search_results.update(set([w.inflected_form for w in list(Inflection_To_Headwords.objects.filter(inflected_form__iexact=query).order_by("inflection")[:limit_inflected])]))
                #set_of_search_results.update(set([w.inflected_form for w in list(Inflection_To_Headwords.objects.filter(inflected_form__iexact=query).order_by("inflection")[:limit_inflected])]))
            elif search_type == 'substring_match':
                match_suffix_wo__ = "icontains"
            elif search_type == 'starts_with':
                match_suffix_wo__ = "istartswith"
            elif search_type == 'ends_with':
                match_suffix_wo__ = "iendswith"
            self.search_tables_generically(query, match_suffix_wo__, set_of_search_results )
            result = list(set_of_search_results)
            return result
        return []




def collect_headword_entries_descrs_from_table_headwords(headword : str = "") -> str:
    result = ""
    try:
        hw : Pali_Word = Pali_Word.objects.get(pk=headword)
    except Pali_Word.DoesNotExist:
        hw = None
    if hw:
        result += hw.simple_text_with_pali() + "<br>"
    return result


def collect_inflected_form_results(word : str) -> str:
    result : str = ""
    hw_list_from_inflected : list[str] = []
    [hw_list_from_inflected.extend(h.headwords.split(",")) for h in list(Inflection_To_Headwords.objects.filter(inflection__iexact=word).order_by("inflection"))]
    for headword in hw_list_from_inflected:
        result += Pali_Word.objects.get(pali_1=headword).simple_text_with_pali() + "<br>"
    return result


def collect_sandhi_results(word : str) -> str:
    sandhis = Sandhi.objects.filter(sandhi=word)
    result = ""
    for sandhi in sandhis:
        result += "sandhi: " + ": " + sandhi.split + "<br>"
    return result


def lookup_word(request : HttpRequest, word : str):
    """Lookup a word in the dictionary dictionary"""
    #print(request.get_full_path())
    template = "lookup_word.html"
    if request.get_full_path().startswith('/dict/dpd/lookup_gd/word/'):
        template = "lookup_word_gd.html"
    word = word.replace("ṁ", "ṃ")
    # TODO: ADD INFLECTED FORMS IN OUTPUT
    #inflected_forms : list[Inflected_Form] = list(Inflected_Form.objects.filter(inflected_form=word))
    result = "<strong>" + word + "</strong><br>"
    #if len(inflected_forms) > 0:
    #    for inflected_form in inflected_forms:
    #        hw : Headword = Headword.objects.get(pk=inflected_form.link_text)
    #        result += hw.desc_html
    if False:
        pass
    else:
        print("collecting from word directly")
        result += collect_headword_entries_descrs_from_table_headwords(word)
    result += collect_sandhi_results(word)
    result += collect_inflected_form_results(word)
    #result += collect_headword_entries_descrs_from_supplementary_tables(word)
    if result == "":
        response = HttpResponse()
        response.status_code = 404
        return response

    context = {
        'body': result,
    }
    return render(request, template, context)
