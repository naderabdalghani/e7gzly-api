from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


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
    def get(self, request):
        """
        Retrieve a list of matches
        """
        return Response('Temporary Data', status=status.HTTP_200_OK)

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
