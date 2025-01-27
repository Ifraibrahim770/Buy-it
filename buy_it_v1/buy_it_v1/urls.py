"""buy_it_v1 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings
from django_email_verification import urls as mail_urls

urlpatterns = [
    path('site/admin/', admin.site.urls),
    path('', include('store.urls')),
    path('accounts/', include('allauth.urls')),
    path('email/', include(mail_urls)),
    path('api-auth/', include('rest_framework.urls'))

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
LOGIN_URL = 'login'
LOGOUT_URL = 'logout'
LOGIN_REDIRECT_URL = 'home'




