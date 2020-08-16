from django.shortcuts import render
from .models import *


# Create your views here.

def store(request):
    products = Product.objects.all()
    carousel_images = CarouselImages.objects.all()
    context = {'products': products,
               'carousel_images': carousel_images}
    return render(request, 'store/store.html', context)


def cart(request):
    context = {}
    return render(request, 'store/cart.html', context)


def checkout(request):
    context = {}
    return render(request, 'store/checkout.html', context)


def view(request, product_id):
    product_info = Product.objects.filter(id=product_id)
    product_description = ProductDescription.objects.filter(product=product_id)
    context = {'product_info': product_info, 'product_description': product_description }
    return render(request, 'store/view_product.html', context)
