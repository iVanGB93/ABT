from django.shortcuts import render, redirect
from .models import Item
from .forms import ItemForm


def items_list(request):
    items = Item.objects.all()
    content = {'items': items}
    return render(request, 'item/items-list.html', content)

def item_detail(request, id):
    item = Item.objects.get(id=id)
    content = {'item': item}
    return render(request, 'item/item-detail.html', content)

def create_item(request):
    form = ItemForm
    content = {'form': form}
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