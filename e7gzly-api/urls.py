"""e7gzly-api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import path
from e7gzly.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('account/login/', LoggingInView.as_view(), name='login'),
    path('account/registration/', RegistrationView.as_view(), name='registration'),
    path('users/', UserView.as_view(), name='users'),
    path('users/authorize/', AuthorizationView.as_view(), name='authorization'),
    path('matches/', MatchView.as_view(), name='matches'),
    path('stadiums/', StadiumView.as_view(), name='stadiums'),
    path('seats/', ReservationView.as_view(), name='reservations')
]
