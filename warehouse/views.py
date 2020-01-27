from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request):
    return render(request, 'warehouse/index.html')

def customer(request):
    return render(request, 'warehouse/customer.html')


def supplier(request):
    return render(request, 'warehouse/supplier.html')