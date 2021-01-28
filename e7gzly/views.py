from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage, InvalidPage
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Admin, User, Match, Seat, Stadium
from .constants import MATCHES_PER_PAGE
from .serializers import MatchSerializer


class RegistrationView(APIView):
    def post(self, request):
        """
        Register a new unauthorized user
        """
        return Response('Temporary Data', status=status.HTTP_200_OK, )


class AuthorizationView(APIView):
    def patch(self, request):
        """
        Authorize a user
        """
        return Response('Temporary Data', status=status.HTTP_200_OK)


class MatchView(APIView):
    serializer_class = MatchSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(name='matches_per_page', description='Defaults to {}'.format(MATCHES_PER_PAGE),
                             required=False, type=int),
            OpenApiParameter(name='page_number', description='Defaults to {}'.format(1),
                             required=False, type=int)
        ],
        responses={status.HTTP_200_OK: MatchSerializer(many=True)},
        examples=[
            OpenApiExample(
                name='Example #1',
                description='Array of retrieved matches',
                value=[
                    {
                        "id": "9",
                        "home_team": "pyramids fc",
                        "away_team": "smouha sc",
                        "date": "2020-10-13T03:10:11Z",
                        "referee": "Damian Aiken",
                        "linesmen": [
                            "Tyler Rowberry",
                            "Hogan Slayton"
                        ],
                        "match_venue": {
                            "id": "1212",
                            "name": "Sohag Stadium",
                            "capacity": 16000,
                            "vip_seats_per_row": 28,
                            "vip_rows": 17
                        },
                        "seats": [
                            {
                                "ticket_id": "01a467324e60460089e38da2e4aaf9fe",
                                "seat_id": "A4"
                            }
                        ]
                    }
                ],
            ),
        ]
    )
    def get(self, request):
        """
        Retrieve a list of matches
        """
        try:
            matches_per_page = int(request.GET.get('matches_per_page', MATCHES_PER_PAGE))
        except ValueError:
            matches_per_page = MATCHES_PER_PAGE
        page_number = request.GET.get('page_number', 1)
        matches = Match.nodes
        paginator = Paginator(matches, matches_per_page)
        try:
            matches = paginator.page(page_number)
        except (PageNotAnInteger, InvalidPage):
            matches = paginator.page(1)
        except EmptyPage:
            matches = paginator.page(paginator.num_pages)
        matches = MatchSerializer(matches, many=True).data
        return Response(data=matches, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Create a new match event
        """
        return Response('Temporary Data', status=status.HTTP_200_OK)

    def patch(self, request):
        """
        Update the details of an existing match
        """
        return Response('Temporary Data', status=status.HTTP_200_OK)


class StadiumView(APIView):
    def get(self, request):
        """
        Retrieve a list of stadiums
        """
        return Response('Temporary Data', status=status.HTTP_200_OK)

    def post(self, request):
        """
        Create a new stadium
        """
        return Response('Temporary Data', status=status.HTTP_200_OK)


class ReservationView(APIView):
    def get(self, request):
        """
        Retrieve vacant/reserved seats for a match
        """
        return Response('Temporary Data', status=status.HTTP_200_OK)

    def post(self, request):
        """
        Reserve a vacant seat for a match
        """
        return Response('Temporary Data', status=status.HTTP_200_OK)

    def delete(self, request):
        """
        Cancel a seat reservation
        """
        return Response('Temporary Data', status=status.HTTP_200_OK)


class LoggingInView(APIView):
    def post(self, request):
        """
        Authenticate a user and provide an access token
        """
        return Response('Temporary Data', status=status.HTTP_200_OK)


class UserView(APIView):
    def get(self, request):
        """
        Retrieve a list of users
        """
        return Response('Temporary Data', status=status.HTTP_200_OK)

    def patch(self, request):
        """
        Update an existing user
        """
        return Response('Temporary Data', status=status.HTTP_200_OK)

    def delete(self, request):
        """
        Delete an existing user
        """
        return Response('Temporary Data', status=status.HTTP_200_OK)
