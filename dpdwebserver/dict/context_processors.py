from django.urls import reverse


class UrlInfo:
    def __init__(self, url_name, title, request):
        self.url_name = url_name
        self.title = title
        self.request = request

    def active_prefix_ws(self):
        if self.is_active():
            return ' active'
        return ''
   
    def disabled_as_text(self):
        if self.is_active():
            return ' disabled'
        return ''

    def is_active(self):
        if(reverse(self.url_name) == self.request.path):
            return True
        return False


def nav_bar_context(request):
    return {'navbar_items': [
        #UrlInfo('niyamata_home_page', 'Home', request),
        UrlInfo('index', 'Pāḷi Dictionaries', request),
        UrlInfo('search_entries_of_dict', 'Search the DPD', request),
    ]
    }
