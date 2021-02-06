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
    UserEditingSerializer, ChangePasswordSerializer, UserAuthorizationSerializer
from .permissions import IsReadOnlyRequest, IsPostRequest, IsPutRequest, IsManager, IsAuthorized, IsAdmin, \
    IsUser, IsDeleteRequest, IsPatchRequest
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
            token = Token().save()
            user.token.connect(token)
            return Response(data={
                'token': token.key,
                'role': user.role
            }, status=status.HTTP_201_CREATED)
        except UniqueProperty as e:
            if 'username' in e.message:
                return Response(data={"username": ["A user with the given username already exists"]},
                                status=status.HTTP_409_CONFLICT)
            if 'email' in e.message:
                return Response(data={"email": ["A user with the given email already exists"]},
                                status=status.HTTP_409_CONFLICT)


class AuthorizationView(APIView):
    permission_classes = [IsAdmin]

    def patch(self, request):
        """
        Authorize a user
        """
        serializer = UserAuthorizationSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['user']
        try:
            user = User.nodes.get(username=username)
        except User.DoesNotExist:
            return Response(data={"user": ["There is no user with the given username"]},
                            status=status.HTTP_404_NOT_FOUND)
        user.authorized = True
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MatchView(APIView):
    permission_classes = [Or(IsReadOnlyRequest,
                             And(Or(IsPostRequest, IsPutRequest), Or(And(IsManager, IsAuthorized), IsAdmin)))]

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
            stadium = Stadium.nodes.get(stadium_id=stadium_id)
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
        match_id = request.data.pop('match_id', None)
        if match_id is None:
            return Response(data={"match_id": ["This field is required"]}, status=status.HTTP_400_BAD_REQUEST)
        stadium_id = request.data.pop('match_venue', None)
        if stadium_id is None:
            return Response(data={"match_venue": ["This field is required"]}, status=status.HTTP_400_BAD_REQUEST)
        serializer = MatchBaseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            match = Match.nodes.get(match_id=match_id)
        except Match.DoesNotExist:
            return Response(data={"match_id": ["There is no match with the given id"]},
                            status=status.HTTP_404_NOT_FOUND)
        try:
            stadium = Stadium.nodes.get(stadium_id=stadium_id)
        except Stadium.DoesNotExist:
            return Response(data={"match_venue": ["There is no stadium with the given id"]},
                            status=status.HTTP_404_NOT_FOUND)
        match.home_team = serializer.validated_data['home_team']
        match.away_team = serializer.validated_data['away_team']
        match.date = serializer.validated_data['date']
        match.referee = serializer.validated_data['referee']
        match.linesmen = serializer.validated_data['linesmen']
        match.save()
        match.match_venue.reconnect(match.match_venue.single(), stadium)
        return Response(data=MatchSerializer(match).data, status=status.HTTP_200_OK)


class StadiumView(APIView):
    permission_classes = [Or(IsReadOnlyRequest,
                             And(IsPostRequest, Or(And(IsManager, IsAuthorized), IsAdmin)))]

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
    permission_classes = [Or(And(Or(IsReadOnlyRequest, IsDeleteRequest), IsUser),
                             And(IsPostRequest, IsAuthorized))]

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
            match = Match.nodes.get(match_id=match_id.hex)
        except Match.DoesNotExist:
            return Response(data={"match_id": ["There is no match with the given id"]},
                            status=status.HTTP_404_NOT_FOUND)
        if not match.match_venue.single().is_valid_seat(seat_id):
            return Response(data={"seat_id": ["Invalid seat_id"]}, status=status.HTTP_400_BAD_REQUEST)
        if not match.is_available_seat(seat_id):
            return Response(data={"seat_id": ["Seat is already reserved"]}, status=status.HTTP_409_CONFLICT)
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
        return Response(data={
            'token': token.key,
            'role': user.role
        }, status=status.HTTP_200_OK)


class UserView(APIView):
    permission_classes = [Or(And(IsReadOnlyRequest, IsAdmin),
                             And(Or(IsPutRequest, IsPatchRequest), IsUser),
                             And(IsDeleteRequest, IsAdmin))]

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
            users = users.filter(authorized=False, role__ne='admin')
        else:
            users = users.filter(role__ne='admin')
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
        user = request.user
        user.first_name = serializer.validated_data['first_name']
        user.last_name = serializer.validated_data['last_name']
        user.birthdate = serializer.validated_data['birthdate']
        user.gender = serializer.validated_data['gender']
        user.city = serializer.validated_data['city']
        user.address = serializer.validated_data.get('address', None)
        user.save()
        return Response(data=UserBaseSerializer(user).data, status=status.HTTP_200_OK)

    def delete(self, request):
        """
        Delete an existing user
        """
        serializer = UserDeletionSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['user']
        try:
            user = User.nodes.get(username=username)
        except User.DoesNotExist:
            return Response(data={"user": ["There is no user with the given username"]},
                            status=status.HTTP_404_NOT_FOUND)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
