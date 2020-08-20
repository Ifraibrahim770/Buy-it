from django.shortcuts import render
from .models import *


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
