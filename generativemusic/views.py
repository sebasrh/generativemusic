from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.

# @login_required
def home(request):
    return render(request, 'index.html')

def page_not_found(request, exception):
    return render(request, '404.html', status=404, context={'exception': exception})