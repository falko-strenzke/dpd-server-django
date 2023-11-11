# views.py
from django.shortcuts import redirect


def redirect_to_dict(request):
    response = redirect('/dict/')
    return response
