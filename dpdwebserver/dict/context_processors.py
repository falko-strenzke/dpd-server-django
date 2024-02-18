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
    # the first argument, 'url_name' refers to the name given in urls.py
    return {'navbar_items': [
        UrlInfo('dpd_page', 'Digital Pāḷi Dictionary', request),
        UrlInfo('search_entries_of_dict', 'Search the DPD', request),
        UrlInfo('search_by_construction', 'Search by Construction', request),
    ]
    }
