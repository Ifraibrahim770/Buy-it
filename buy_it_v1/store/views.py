import random

from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .OrderProcessing import Processorder
from .models import *
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.forms import UserCreationForm
from .forms import CreateUserForm, AuthenticateUserForm, ResetPasswordForm, PhoneForm, VerifyForm
import requests
from requests.auth import HTTPBasicAuth
import json
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.utils.encoding import *
from django.utils.http import *
from django.contrib.sites.shortcuts import *
from .utils import token_generator
from allauth.socialaccount.models import SocialAccount
from .serializers import ProductSerializer

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
            # if not user.is_active:
            # messages.success(request, 'Error, please verify your email')
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
                messages.info(request, "that email is already registered", extra_tags="error")

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
        # print('the google user is', request.user)

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

        # test=' {"id": "3720852601356272", "email": "ibrahimdiba87@gmail.com", "name": "Ibrahim Diba", "first_name": "Ibrahim", "last_name": "Diba"},'
        # json_data = json.loads(test)
        # print('json_data',json_data)
        if request.user.email == '':
            extra_data = SocialAccount.objects.values_list('extra_data').get(user=request.user.pk)
            object_string = str(extra_data)
            non_bracket = object_string.replace("(", "")
            non_other_bracket = non_bracket.replace(")", "")

            valid_json = non_other_bracket.replace('\'', '"')
            really_valid_json = valid_json[:-1]
            print('extra', really_valid_json)
            son_data = json.loads(really_valid_json)
            print('json_data', son_data["email"])
            mail = son_data["email"]
            user = User.objects.get(username=request.user.username)
            user.email = mail
            user.save()
        else:
            mail = request.user.email

        if ShippingAddress.objects.filter(customer=customer).exists():
            shippingAddressExist = 'True'
            address = ShippingAddress.objects.values_list('address', flat=True).last()
            state = ShippingAddress.objects.values_list('state', flat=True).last()
            city = ShippingAddress.objects.values_list('city', flat=True).last()

            username = request.user.username
            email = mail
            disabled = 'disabled'

            print("THESE ARE THE DETAILS FOR THE LOGGED IN USER", username, email)

        else:
            shippingAddressExist = 'False'
            state = ''
            address = ''
            city = ''
            username = request.user.username
            email = mail
            disabled = 'disabled'

    else:
        items = []
    context = {'name': username, 'email': email, 'items': items,
               'order': order,
               'cartItems': cartItems,
               'shippingAddressExist': shippingAddressExist,
               'address': address,
               'state': state,
               'city': city,
               'form_function': disabled}

    print("this is my email value", email)
    return render(request, 'store/checkout.html', context)


def view(request, product_id):
    # product_information
    product_info = Product.objects.filter(id=product_id)
    product_description = ProductDescription.objects.filter(product=product_id)
    product_images = ProductImage.objects.filter(product=product_id)
    order, created = Order.objects.get_or_create(customer=request.user.customer, complete=False)
    cartItems = order.get_cart_items

    product_reviews = ProductReview.objects.filter(product=product_id)

    # similar_products
    product_category = Product.objects.values_list('category', flat=True).get(pk=product_id)
    similar_products = Product.objects.filter(category=product_category)
    category_options = ProductCategory.objects.all()

    # context
    context = {'product_info': product_info,
               'product_reviews': product_reviews,
               'product_id': product_id,
               'cartItems': cartItems,
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
    context = {'form': form}

    return render(request, 'store/password_reset.html', context)


def search(request):
    if request.method == 'GET':
        search_term = request.GET.get('search')
        results = Product.objects.filter(name__icontains=search_term)

        print(results)

    context = {'results': results}

    return render(request, 'store/search_results.html', context)


def saveShippingInfo(request):
    if request.method == 'GET':
        address = request.GET.get('address')
        city = request.GET.get('city')
        state = request.GET.get('state')

        print("method entered", address)

        customer = request.user.customer

        if request.user.email == '':
            email = request.GET.get('email')
            user = User.objects.get(username=request.user.username)
            user.email = email
            user.save()

        if ShippingAddress.objects.filter(customer=customer).exists():
            shipping_info = ShippingAddress.objects.filter(customer=customer)
            shipping_info.update(address=address)
            shipping_info.update(city=city)
            shipping_info.update(state=state)
        else:
            shipping_info = ShippingAddress.objects.create(customer=customer)
            shipping_info.address = address
            shipping_info.city = city
            shipping_info.state = state

            shipping_info.save()

        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items

        print("tha needed info", address, state, city)

        messages.info(request, "Your Order is Processed!!! Pending Confirmation...")
        Processorder(request)

    context = {'items': items,
               'order': order,
               'cartItems': cartItems}
    return redirect('store')


def ProcessOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    customer = request.user.customer
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    order.transaction_id = transaction_id
    order.complete = True
    order.save()
    return JsonResponse('Item was Added', safe=False)


def saveReview(request):
    if request.method == 'GET':
        star = request.GET.get('rating')
        comment = request.GET.get('comment')
        customer = request.user.customer
        product_id = request.GET.get('product_id')

        # order_items = OrderItem.objects.filter(order=orders, product=product_id)

        if isProductPurchased(request, product_id):
            product = Product.objects.get(id=product_id)
            Review = ProductReview.objects.create(customer=customer, product=product)
            Review.stars = star
            Review.review = comment
            Review.save()
            print('Your shit has been saved!!!')
        else:
            print('You cant review a product you havent purchased')

    return render(request, 'store/search_results.html')


def verifyPhoneNumber(request):
    phone_form = PhoneForm()
    code_form = VerifyForm()
    context = {'phone_form': phone_form,
               'code_form': code_form}
    if request.method == 'POST':
        phone_number = request.POST.get('your_number')
        if phone_number:
            print('the number is this', phone_number)
            phone = str(phone_number)
            user = UserPhoneNumbers.objects.filter(phone_no=phone)
            if user.exists():
                return JsonResponse('Phone Number Already exist', safe=False)
            else:
                key = sendotp(phone)
                final_message = 'Your MarketPlace Verification Code is ' + str(key)
                request.session['otp_phone'] = phone
                non_zero_phone = phone[1:]
                cleaned_phone = '254' + non_zero_phone
                print('cleaned_phone', cleaned_phone)
                link = 'http://bauersms.co.ke/adminx/api.php?apikey=5SWegOcd6oQWhad2&apitext=[Your message]&tel=[Your+Recipients]&method=sendsms'
                link = link.replace('[Your+Recipients]', cleaned_phone)
                link = link.replace('[Your message]', str(key))
                print("the final link is", link)

                response = requests.post(link)
                print(response.text)

                # sendSMS(cleaned_phone, key)
                messages.info(request, "Code Sent, Kindly Check Your Phone")
            if key:
                old = MobileVerification.objects.filter(phone_no=phone)
                if old.exists():
                    old = old.first()
                    count = old.count

                    if count > 5:
                        print("Otp limit exceeded")
                        return
                    old.count = count + 1
                    old.save()

                MobileVerification.objects.create(
                    phone_no=phone,
                    verification_code=key

                )
                print("the generated key_value is", key)
            else:
                return JsonResponse('Error Generating OTP', safe=False)

        else:
            verification_code = request.POST.get('verification_code')
            phoneNo = request.session['otp_phone']

            if int(phoneNo) & int(verification_code):
                old = MobileVerification.objects.filter(phone_no=phoneNo)
                if old.exists():
                    old = old.first()
                    otp = old.verification_code

                    if str(verification_code) == str(otp):
                        customer = request.user.customer
                        UserPhoneNumbers.objects.create(
                            customer=customer,
                            phone_no=phoneNo,
                            verified=True
                        )
                        messages.info(request, "Verification Successful!!!")
                        return redirect('store')
                    else:
                        print("OTP is invalid try again...or else")

    return render(request, 'store/verifyPhoneNumber.html', context)


def sendotp(phone_number):
    if phone_number:
        key = random.randint(999, 9999)
        return key
    else:
        return False


def sendSMS(phone_number, code):
    url = "https://twilio-sms.p.rapidapi.com/2010-04-01/Accounts/undefined/Messages.json"

    querystring = {"from": "7765", "body": code, "to": phone_number}

    headers = {
        'x-rapidapi-key': "511e5b32d9msh770fba0b2915986p182943jsn6ece95b62232",
        'x-rapidapi-host': "twilio-sms.p.rapidapi.com"
    }

    response = requests.request("POST", url, headers=headers, params=querystring)

    print(response.text)


def Categories(request, category_name):
    print(category_name)

    cat = ProductCategory.objects.get(categoryName=category_name)

    print(cat.id)
    results = Product.objects.filter(category=cat.id)

    context = {'results': results,
               'category_name': category_name}
    return render(request, 'store/ProductCategory.html', context)


def isProductPurchased(request, product_id):
    customer = request.user.customer
    orders = Order.objects.filter(customer=customer, complete=True)
    for order in orders:
        order_items = OrderItem.objects.filter(order=order.pk, product=product_id)

        if order_items.exists():
            return True
        else:
            return False


def Stalls(request):
    stalls = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    return render(request, 'store/Stalls.html', {"stalls": stalls})


# API REQUESTS
@api_view(['GET'])
def ProductApi(request):
    products = Product.objects.all()

    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def ProductApiDetail(request, pk):
    products = Product.objects.get(id=pk)

    serializer = ProductSerializer(products, many=False)
    return Response(serializer.data)
