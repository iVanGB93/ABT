from django.shortcuts import render, redirect
from .models import Item, Item_List
from .forms import ItemForm


def items_list(request):
    items = Item_List.objects.all()
    content = {'items': items}
    return render(request, 'item/items-list.html', content)

def item_detail(request, id):
    item = Item_List.objects.get(id=id)
    items = Item.objects.filter(list=item)
    content = {'item': item, 'items': items}
    return render(request, 'item/item-detail.html', content)

def create_item(request):
    form = ItemForm
    content = {'icon': 'error', 'form': form}
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('item:items_list')
        else:
            error = form.errors
            print("ERROR", error)
            content['message'] = error
    return render(request, 'item/create-item.html', content)

def delete_item(request, id):
    item = Item_List.objects.get(id=id)
    item.delete()
    return redirect('item:items_list')