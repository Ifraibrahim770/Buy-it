from django.urls import path
from . import views
from .views import EmailVerification

urlpatterns=[
    path('', views.store, name="store"),
    path('cart/', views.cart, name="cart"),
    path('checkout/', views.checkout, name="checkout"),
    path('<int:product_id>', views.view, name="view_item"),
    path ('update_item/', views.UpdateItem, name="update_item"),
    path('register/', views.sign_up, name="register"),
    path ('login/', views.sign_in, name="login"),
    path('logout', views.logout_request, name='logout'),
    path('activate/<uidb64>/<token>', EmailVerification.as_view(), name='activate'),
    path('reset/', views.reset_password, name='reset'),
    path('search/', views.search, name='search'),
    path('search/<int:product_id>', views.view, name="view_item"),
    #path(r'^(?P<product_id>[0-9]+)/$', views.view, name="view_item")

]