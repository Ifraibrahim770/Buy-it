from django.urls import path
from . import views

urlpatterns=[
    path('', views.store, name="store"),
    path('cart/', views.cart, name="cart"),
    path('checkout/', views.checkout, name="checkout"),
    path('<int:product_id>', views.view, name="view_item"),
    path ('update_item/', views.UpdateItem, name="update_item"),
    path('register/', views.sign_up, name="register"),
    path ('login/', views.sign_in, name="login")
    #path(r'^(?P<product_id>[0-9]+)/$', views.view, name="view_item")

]