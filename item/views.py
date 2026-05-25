from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Item, Item_List
from .forms import ItemForm
from business.models import Business


def items_list(request):
    items = Item_List.objects.all()
    content = {'items': items}
    return render(request, 'item/items-list.html', content)

def item_detail(request, id):
    item = Item_List.objects.get(id=id)
    items = Item.objects.filter(list=item)
    content = {'item': item, 'items': items}
    return render(request, 'item/item-detail.html', content)

@login_required
def create_item(request, business_name):
    business = get_object_or_404(Business, name=business_name)
    form = ItemForm()
    content = {'form': form, 'business': business}
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.business = business
            item.save()
            return redirect('business:business_items', business_name=business_name)
        else:
            content['form'] = form
            content['message'] = form.errors
    return render(request, 'item/create-item.html', content)

def delete_item(request, id):
    item = Item_List.objects.get(id=id)
    item.delete()
    return redirect('item:items_list')