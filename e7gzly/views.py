from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage, InvalidPage
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Match, Stadium
from .constants import MATCHES_PER_PAGE
from .serializers import MatchSerializer, MatchBaseSerializer


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
        stadium_id = request.data.pop('match_venue', None)
        if stadium_id is None:
            return Response(data={"match_venue": ["This field is required"]}, status=status.HTTP_400_BAD_REQUEST)
        serializer = MatchBaseSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            stadium = Stadium.nodes.get(_id=stadium_id)
        except Stadium.DoesNotExist:
            return Response(data={"match_venue": ["There is no stadium with the given id"]},
                            status=status.HTTP_404_NOT_FOUND)
        match = Match.create(serializer.validated_data)[0]
        match.match_venue.connect(stadium)
        return Response(data=MatchSerializer(match).data, status=status.HTTP_201_CREATED)

    def put(self, request):
        """
        Update the details of an existing match
        """
        match_id = request.data.pop('_id', None)
        if match_id is None:
            return Response(data={"_id": ["This field is required"]}, status=status.HTTP_400_BAD_REQUEST)
        stadium_id = request.data.pop('match_venue', None)
        if stadium_id is None:
            return Response(data={"match_venue": ["This field is required"]}, status=status.HTTP_400_BAD_REQUEST)
        serializer = MatchBaseSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            match = Match.nodes.get(_id=match_id)
        except Match.DoesNotExist:
            return Response(data={"_id": ["There is no match with the given id"]},
                            status=status.HTTP_404_NOT_FOUND)
        try:
            stadium = Stadium.nodes.get(_id=stadium_id)
        except Stadium.DoesNotExist:
            return Response(data={"match_venue": ["There is no stadium with the given id"]},
                            status=status.HTTP_404_NOT_FOUND)
        match = match.update(serializer.validated_data)
        match.match_venue.reconnect(match.match_venue.single(), stadium)
        return Response(status=status.HTTP_200_OK)


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
