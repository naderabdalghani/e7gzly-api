from django.urls import path

from e7gzly.consumers import *

websocket_urlpatterns = [
    path('match/reservations/<str:match_id>', ReservationsConsumer.as_asgi())
]
