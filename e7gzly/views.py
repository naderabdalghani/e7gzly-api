from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage, InvalidPage
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Match, Stadium
from .constants import MATCHES_PER_PAGE
from .serializers import MatchSerializer, MatchBaseSerializer, CustomResponseSerializer


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
                name='Example',
                description='Array of retrieved matches',
                value=[
                    {
                        "_id": "f23da8a82a4e4baf938e6f03445e7f51",
                        "home_team": "pyramids fc",
                        "away_team": "smouha sc",
                        "date": "2020-10-13T03:10:11Z",
                        "referee": "Damian Aiken",
                        "linesmen": [
                            "Tyler Rowberry",
                            "Hogan Slayton"
                        ],
                        "match_venue": {
                            "_id": "7b4d0bb5ceb649f087f7a90a497b34f9",
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

    @extend_schema(
        responses={
            status.HTTP_201_CREATED: MatchSerializer(),
            status.HTTP_400_BAD_REQUEST: CustomResponseSerializer({'<bad_field>': '<description>'})
        },
        examples=[
            OpenApiExample(
                name='Example',
                request_only=True,
                value={
                    "home_team": "pyramids fc",
                    "away_team": "al ahly sc",
                    "date": "2021-03-19T07:00:00Z",
                    "referee": "Mohammad Abdo",
                    "linesmen": [
                        "Tyler Charlie",
                        "Hogan McDonald"
                    ],
                    "match_venue": "4e6cc1704b38499eb36ec29086d46c48"
                }
            ),
            OpenApiExample(
                name='Example',
                response_only=True,
                value={
                    "_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "home_team": "pyramids fc",
                    "away_team": "al ahly sc",
                    "date": "2021-03-19T07:00:00Z",
                    "referee": "Mohammad Abdo",
                    "linesmen": [
                        "Tyler Charlie",
                        "Hogan McDonald"
                    ],
                    "match_venue": {
                        "_id": "4e6cc1704b38499eb36ec29086d46c48",
                        "name": "Borg El Arab Stadium",
                        "vip_rows": 20,
                        "vip_seats_per_row": 10,
                        "capacity": 86000
                    },
                    "seats": []
                },
            )
        ]
    )
    def post(self, request):
        """
        Create a new match event
        """
        stadium_id = request.data.pop('match_venue', None)
        if stadium_id is None:
            return Response(data={"match_venue": ["This field is required"]}, status=status.HTTP_400_BAD_REQUEST)
        serializer = MatchBaseSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        stadium = Stadium.nodes.get_or_none(_id=stadium_id)
        if stadium is None:
            return Response(data={"match_venue": ["There is no stadium with the given id"]},
                            status=status.HTTP_404_NOT_FOUND)
        match = Match.create(serializer.validated_data)[0]
        match.match_venue.connect(stadium)
        return Response(data=MatchSerializer(match).data, status=status.HTTP_201_CREATED)

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
