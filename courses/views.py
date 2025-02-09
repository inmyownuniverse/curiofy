from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required(login_url='accounts:login')
def get_started(request):
    return render(request, 'courses/get_started.html')

@login_required(login_url='accounts:login')
def science(request):
    return render(request, 'courses/science.html')

@login_required(login_url='accounts:login')
def mathematics(request):
    return render(request, 'courses/mathematics.html')

@login_required(login_url='accounts:login')
def engineering(request):
    return render(request, 'courses/engineering.html')  

@login_required(login_url='accounts:login')
def technology(request):
    return render(request, 'courses/technology.html')   

