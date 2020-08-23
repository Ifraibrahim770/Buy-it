from django.urls import path
from . import views

urlpatterns=[
    path('', views.store, name="store"),
    path('cart/', views.cart, name="cart"),
    path('checkout/', views.checkout, name="checkout"),
    path('<int:product_id>', views.view, name="view_item"),
    path ('update_item/', views.UpdateItem, name="update_item")
    #path(r'^(?P<product_id>[0-9]+)/$', views.view, name="view_item")

]