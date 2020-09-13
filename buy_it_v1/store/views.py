from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View

from .models import *
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.forms import UserCreationForm
from .forms import CreateUserForm, AuthenticateUserForm,ResetPasswordForm
import requests
from requests.auth import HTTPBasicAuth
import json
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.utils.encoding import *
from django.utils.http import *
from django.contrib.sites.shortcuts import *
from .utils import token_generator

import socket

socket.getaddrinfo('127.0.0.1', 8000)
from django_email_verification import sendConfirm


# Create your views here.


def sign_in(request):
    form = AuthenticateUserForm()
    context = {'form': form}
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        print(user)
        print(username, password)

        if user is not None:
            customer = Customer.objects.get_or_create(user=user)
            login(request, user)
            return redirect('store')
        else:
            #if not user.is_active:
                #messages.success(request, 'Error, please verify your email')
            return render(request, 'store/login.html', context)
    #
    # print(username, password)
    print('DA USER IS ', request.user)

    return render(request, 'store/login.html', context)


def sign_up(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password1')
            if email and User.objects.filter(email=email).exclude(username=username).exists():
                messages.info(request, "that email is already registered",extra_tags="error")

            else:
                user = get_user_model().objects.create(username=username, email=email)
                user.set_password(password)
                user.is_active = False
                user.save()
                # print (form)
                # print(email, password)
                # form.save()
                # user = get_user_model().objects.create(username=username, password=password, email=email)
                # print('sending verification to email', email)
                # sendConfirm(user)
                # print('verification sent!!!!!')
                # uidb64 = force_bytes(urlsafe_base64_encode(user.pk))
                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                token = token_generator.make_token(user)

                ts = datetime.datetime.now().timestamp()

                domain = get_current_site(request).domain
                cleaned_domain = domain[0: 21]
                link = reverse('activate', kwargs={'uidb64': uidb64, 'token': token_generator.make_token(user)})
                activate_url = cleaned_domain + link
                print(cleaned_domain)
                email_subject = 'Activate Your Market Place Account'
                email_body = 'Hi ' + user.username + ' Please use this link to verify your Market Place Account\n' + activate_url
                email = EmailMessage(
                    email_subject,
                    email_body,
                    'noreply@marketplace.com',
                    [email],
                )

                email.send(fail_silently=False)
                messages.success(request, 'Account was created Successfully!!')
                return redirect('login')
    context = {'form': form}
    return render(request, 'store/register.html', context)


def store(request):
    if request.user.is_authenticated:
        #print('the google user is', request.user)

        try:
            customer = request.user.customer
        except ObjectDoesNotExist:
            customer = Customer.objects.create(user=request.user, name=str(request.user))
        else:
            customer = request.user.customer

        # customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0}
        cartItems = order['get_cart_items']
    products = Product.objects.all()
    carousel_images = CarouselImages.objects.all()
    category_options = ProductCategory.objects.all()

    context = {'products': products,
               'carousel_images': carousel_images,
               'category_options': category_options,
               'cartItems': cartItems}
    return render(request, 'store/store.html', context)


def cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
    context = {'items': items,
               'order': order,
               'cartItems': cartItems}
    return render(request, 'store/cart.html', context)


def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
    context = {'items': items,
               'order': order,
               'cartItems': cartItems}
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

    # context
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

    customer = request.user.customer
    product = Product.objects.get(id=product_id)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)
    print('initial ', orderItem.quantity)

    if action == 'add':
        orderItem.quantity = orderItem.quantity + 1
        messages.success(request, 'Your product was added to the cart!!!')
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    if orderItem.quantity <= 0:
        orderItem.delete()
    else:
        orderItem.save()

    return JsonResponse('Item was Added', safe=False)


def logout_request(request):
    logout(request)
    messages.info(request, "Logged out successfully!")
    return redirect('login')


class EmailVerification(View):
    def get(self, request, uidb64, token):
        # uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        user_primary_key = urlsafe_base64_decode(uidb64)
        cleaned_pk = user_primary_key.decode("utf-8")
        print("this is the decoded primary key", cleaned_pk)

        user = User.objects.get(pk=cleaned_pk)
        user.is_active = True
        user.save()
        return redirect('login')


def reset_password(request):
    form = ResetPasswordForm()
    context = {'form':form}

    return render(request, 'store/password_reset.html', context)


def search(request):
    if request.method == 'GET':
        search_term = request.GET.get('search')
        results = Product.objects.filter(name__icontains=search_term)

        print(results)

    context = {'results':results}

    return render(request, 'store/search_results.html', context)


