from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage, InvalidPage
from neomodel import UniqueProperty
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_condition import And, Or
from .models import Match, Stadium, User, Token
from .constants import MATCHES_PER_PAGE
from .serializers import MatchSerializer, MatchBaseSerializer, UserBaseSerializer, UserSerializer, \
    LoginDataSerializer, StadiumSerializer, StadiumBaseSerializer
from .permissions import IsReadOnlyRequest, IsPostRequest, IsPutRequest, IsManager, IsAuthorized, IsAdmin
from django.contrib.auth.hashers import make_password, check_password


class RegistrationView(APIView):
    def post(self, request):
        """
        Register a new unauthorized user
        """
        serializer = UserBaseSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user_data = serializer.validated_data
        user_data['password'] = make_password(user_data['password'])
        try:
            user = User.create(user_data)[0]
            return Response(data=UserSerializer(user).data, status=status.HTTP_201_CREATED)
        except UniqueProperty as e:
            if 'username' in e.message:
                return Response(data="A user with the given username already exists", status=status.HTTP_409_CONFLICT)
            if 'email' in e.message:
                return Response(data="A user with the given email already exists", status=status.HTTP_409_CONFLICT)


class AuthorizationView(APIView):
    permission_classes = [IsAdmin]

    def patch(self, request):
        """
        Authorize a user
        """
        try:
            user_id = request.query_params['user_id']
        except KeyError:
            return Response(data={"user_id": ["This field is required"]}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.nodes.get(_id=user_id)
        except User.DoesNotExist:
            return Response(data={"user_id": ["There is no user with the given id"]}, status=status.HTTP_404_NOT_FOUND)
        user.authorized = True
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MatchView(APIView):
    permission_classes = [Or(And(IsReadOnlyRequest),
                             And(Or(IsPostRequest, IsPutRequest), And(IsManager, IsAuthorized)))]

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
            return Response(data={"_id": ["There is no match with the given id"]}, status=status.HTTP_404_NOT_FOUND)
        try:
            stadium = Stadium.nodes.get(_id=stadium_id)
        except Stadium.DoesNotExist:
            return Response(data={"match_venue": ["There is no stadium with the given id"]},
                            status=status.HTTP_404_NOT_FOUND)
        match = match.update(serializer.validated_data)
        match.match_venue.reconnect(match.match_venue.single(), stadium)
        return Response(status=status.HTTP_200_OK)


class StadiumView(APIView):
    permission_classes = [Or(And(IsReadOnlyRequest),
                             And(IsPostRequest, And(IsManager, IsAuthorized)))]

    def get(self, request):
        """
        Retrieve a list of all stadiums
        """
        return Response(data=StadiumBaseSerializer(Stadium.nodes, many=True).data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Create a new stadium
        """
        serializer = StadiumBaseSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        stadium = Stadium.create(serializer.validated_data)[0]
        return Response(data=StadiumSerializer(stadium).data, status=status.HTTP_201_CREATED)


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


class LoggingInView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        """
        Authenticate a user and provide an access token
        """
        serializer = LoginDataSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        try:
            user = User.nodes.get(username=username)
        except User.DoesNotExist:
            return Response(data="Incorrect credentials", status=status.HTTP_401_UNAUTHORIZED)
        if not check_password(password, user.password):
            return Response(data="Incorrect credentials", status=status.HTTP_401_UNAUTHORIZED)
        token = user.token.single()
        if token is not None:
            token.delete()
        token = Token().create({})[0].save()
        user.token.connect(token)
        return Response(data={'token': token.key}, status=status.HTTP_200_OK)


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
