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
from django.urls import path
from e7gzly.views import *

urlpatterns = [
    path('account/login/', LoggingInView.as_view(), name='login'),
    path('account/registration/', RegistrationView.as_view(), name='registration'),
    path('account/authorization/', AuthorizationView.as_view(), name='authorization'),
    path('users/', UserView.as_view(), name='users'),
    path('user/', UserDetailsView.as_view(), name='user details'),
    path('matches/', MatchView.as_view(), name='matches'),
    path('match/', MatchDetailsView.as_view(), name='match details'),
    path('stadiums/', StadiumView.as_view(), name='stadiums'),
    path('reservations/', ReservationView.as_view(), name='reservations')
]
