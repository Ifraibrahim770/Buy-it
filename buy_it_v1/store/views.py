from django.shortcuts import render
from .models import *
from django.http import HttpResponse, JsonResponse
import requests
from requests.auth import HTTPBasicAuth
import json

# Create your views here.

def store(request):
    products = Product.objects.all()
    carousel_images = CarouselImages.objects.all()
    category_options = ProductCategory.objects.all()
    context = {'products': products,
               'carousel_images': carousel_images,
               'category_options': category_options}
    return render(request, 'store/store.html', context)


def cart(request):
    if request.user.is_authenticated:
        customer =request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items =order.orderitem_set.all()
    else:
        items = []
    context = {'items':items,
               'order':order}
    return render(request, 'store/cart.html', context)


def checkout(request):
    context = {}
    return render(request, 'store/checkout.html', context)


def view(request, product_id):
    # product_information
    product_info = Product.objects.filter(id=product_id)
    product_description = ProductDescription.objects.filter(product=product_id)
    product_images = ProductImage.objects.filter(product=product_id)

    # similar_products
    product_category = Product.objects.values_list('category', flat=True).get(pk=product_id)
    similar_products = Product.objects.filter(category=product_category)
    category_options = ProductCategory.objects.all()

    #context99
    context = {'product_info': product_info,
               'product_description': product_description,
               'product_images': product_images,
               'category_options': category_options,
               'similar_products': similar_products}
    return render(request, 'store/view_product.html', context)


def UpdateItem(request):
    data = json.loads(request.body)
    product_id = data['productID']
    action = data['action']
    print('productID', product_id)
    print('action', data['action'])

    customer=request.user.customer
    product= Product.objects.get(id=product_id)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)
    print('initial ',orderItem.quantity)

    if action == 'add':
        orderItem.quantity = orderItem.quantity + 1
        print (orderItem.quantity)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    if orderItem.quantity <= 0:
        orderItem.delete

    orderItem.save()

    return JsonResponse('Item was Added', safe=False)

