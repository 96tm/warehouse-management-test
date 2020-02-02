from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    return render(request, 'warehouse/index.html')


def order(request):

    return render(request, 'warehouse/order.html')


def supplier(request):
    return render(request, 'warehouse/supplier.html')