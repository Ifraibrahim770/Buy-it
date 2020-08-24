from django.shortcuts import render,redirect
from .models import *
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.forms import UserCreationForm
from .forms import CreateUserForm,AuthenticateUserForm
import requests
from requests.auth import HTTPBasicAuth
import json
from django.contrib.auth import authenticate,login,logout

# Create your views here.


def sign_in(request):
    form = AuthenticateUserForm()
    context = {'form': form}
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            customer = Customer.objects.get_or_create(user=user)
            customer.save()
            login(request, user)
            return redirect('store')
        else:
            return render(request, 'store/login.html', context)
    #
        #print(username, password)

    return render(request, 'store/login.html', context)


def sign_up(request):
    form = CreateUserForm()
    if request.method =='POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    context = {'form': form}
    return render(request, 'store/register.html', context)


def store(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total':0, 'get_cart_items':0}
        cartItems = order['get_cart_items']
    products = Product.objects.all()
    carousel_images = CarouselImages.objects.all()
    category_options = ProductCategory.objects.all()

    context = {'products': products,
               'carousel_images': carousel_images,
               'category_options': category_options,
               'cartItems':  cartItems}
    return render(request, 'store/store.html', context)


def cart(request):
    if request.user.is_authenticated:
        customer =request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items =order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
    context = {'items':items,
               'order':order,
               'cartItems':cartItems}
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




