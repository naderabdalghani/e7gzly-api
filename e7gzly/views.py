from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage, InvalidPage
from django.utils import timezone
from neomodel import UniqueProperty
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_condition import And, Or
from .models import Match, Stadium, User, Token, Seat
from .constants import TICKET_CANCELLATION_WINDOW
from .serializers import MatchSerializer, MatchBaseSerializer, UserBaseSerializer, UserSerializer, \
    LoginDataSerializer, StadiumSerializer, StadiumBaseSerializer, SeatSerializer, SeatReservationSerializer, \
    ReservationCancellationSerializer, UsersRetrievalSerializer, MatchesRetrievalSerializer, UserDeletionSerializer, \
    UserEditingSerializer, ChangePasswordSerializer
from .permissions import IsReadOnlyRequest, IsPostRequest, IsPutRequest, IsManager, IsAuthorized, IsAdmin, \
    IsUser, IsDeleteRequest
from django.contrib.auth.hashers import make_password, check_password


class RegistrationView(APIView):
    def post(self, request):
        """
        Register a new unauthorized user
        """
        serializer = UserBaseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
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
        serializer = MatchesRetrievalSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        matches_per_page = serializer.validated_data['matches_per_page']
        page_number = serializer.validated_data['page_number']
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
        serializer.is_valid(raise_exception=True)
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
        serializer.is_valid(raise_exception=True)
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
        return Response(data=MatchSerializer(match).data, status=status.HTTP_200_OK)


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
        serializer.is_valid(raise_exception=True)
        stadium = Stadium.create(serializer.validated_data)[0]
        return Response(data=StadiumSerializer(stadium).data, status=status.HTTP_201_CREATED)


class ReservationView(APIView):
    permission_classes = [Or(And(IsReadOnlyRequest, IsUser),
                             And(Or(IsPostRequest, IsDeleteRequest), IsAuthorized))]

    def get(self, request):
        """
        Retrieve reserved seats for a user
        """
        return Response(data=SeatSerializer(request.user.reservations.all(), many=True).data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Reserve a vacant seat for a match
        """
        serializer = SeatReservationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        match_id = serializer.validated_data['match_id']
        seat_id = serializer.validated_data['seat_id']
        try:
            match = Match.nodes.get(_id=match_id.hex)
        except Match.DoesNotExist:
            return Response(data={"match_id": ["There is no match with the given id"]},
                            status=status.HTTP_404_NOT_FOUND)
        if not match.match_venue.single().is_valid_seat(seat_id):
            return Response(data={"seat_id": ["Invalid seat_id"]}, status=status.HTTP_400_BAD_REQUEST)
        if not match.is_available_seat(seat_id):
            return Response(data={"seat_id": ["Seat already reserved"]}, status=status.HTTP_409_CONFLICT)
        seat = Seat(seat_id=seat_id).save()
        user = request.user
        user.reservations.connect(seat)
        seat.match.connect(match)
        return Response(data=SeatSerializer(seat).data, status=status.HTTP_201_CREATED)

    def delete(self, request):
        """
        Cancel a reservation
        """
        serializer = ReservationCancellationSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        user = request.user
        try:
            reservation = user.reservations.get(ticket_id=serializer.validated_data['ticket_id'].hex)
        except Seat.DoesNotExist:
            return Response(data={"ticket_id": ["There is no reservation with the given id"]},
                            status=status.HTTP_404_NOT_FOUND)
        if timezone.now() > reservation.match.single().date - timezone.timedelta(days=TICKET_CANCELLATION_WINDOW):
            return Response(data={
                "ticket_id": [
                    "Reservations can be cancelled in at least {} days before the corresponding event"
                    .format(TICKET_CANCELLATION_WINDOW)
                ]
            }, status=status.HTTP_403_FORBIDDEN)
        reservation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class LoggingInView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        """
        Authenticate a user and provide an access token
        """
        serializer = LoginDataSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
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
        token = Token().save()
        user.token.connect(token)
        return Response(data={'token': token.key}, status=status.HTTP_200_OK)


class UserView(APIView):
    def get(self, request):
        """
        Retrieve a list of users
        """
        serializer = UsersRetrievalSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        unauthorized = serializer.validated_data['unauthorized']
        users_per_page = serializer.validated_data['users_per_page']
        page_number = serializer.validated_data['page_number']
        users = User.nodes
        if unauthorized:
            users = users.filter(authorized=False)
        paginator = Paginator(users, users_per_page)
        try:
            users = paginator.page(page_number)
        except (PageNotAnInteger, InvalidPage):
            users = paginator.page(1)
        except EmptyPage:
            users = paginator.page(paginator.num_pages)
        users = UserBaseSerializer(users, many=True).data
        return Response(data=users, status=status.HTTP_200_OK)

    def patch(self, request):
        """
        Update user password
        """
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not check_password(serializer.validated_data['old_password'], request.user.password):
            return Response(data={"old_password": ["Incorrect old password"]}, status=status.HTTP_403_FORBIDDEN)
        user = request.user
        user.password = make_password(serializer.validated_data['new_password'])
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self, request):
        """
        Update user personal info
        """
        serializer = UserEditingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user.update(serializer.validated_data)
        return Response(data=UserBaseSerializer(user).data, status=status.HTTP_200_OK)

    def delete(self, request):
        """
        Delete an existing user
        """
        serializer = UserDeletionSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        user_id = serializer.validated_data['user_id']
        try:
            user = User.nodes.get(_id=user_id.hex)
        except User.DoesNotExist:
            return Response(data={"user_id": ["There is no user with the given id"]},
                            status=status.HTTP_404_NOT_FOUND)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
