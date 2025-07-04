from django.shortcuts import render
from .models import Business


def business_list(request):
    business_list = Business.objects.filter(owners=request.user).order_by('name')
    context = { 'business_list': business_list }
    return render(request, 'business/business-list.html', context)

def business_detail(request, business_id):
    business = Business.objects.get(id=business_id)
    context = { 'business': business }
    return render(request, 'business/business-detail.html', context)