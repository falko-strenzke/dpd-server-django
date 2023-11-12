# views.py
from django.shortcuts import redirect


def redirect_to_dpd(request):
    response = redirect('/dict/dpd/')
    return response
