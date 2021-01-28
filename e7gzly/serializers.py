from rest_framework import serializers
from .constants import NAME_MAX_LEN, STADIUM_NAME_MAX_LEN, CITIES, GENDERS, TEAMS, ROLES, \
    SEAT_ID_MAX_LEN, ADDRESS_MAX_LEN


class AdminSerializer(serializers.Serializer):
    _id = serializers.UUIDField(allow_null=False, read_only=True)
    username = serializers.CharField(required=True, allow_null=False, allow_blank=False, max_length=NAME_MAX_LEN)
    email = serializers.EmailField(required=True, allow_null=False, allow_blank=False)
    password = serializers.CharField(required=True, allow_null=False, allow_blank=False)
    first_name = serializers.CharField(required=True, allow_null=False, allow_blank=False, max_length=NAME_MAX_LEN)
    last_name = serializers.CharField(required=True, allow_null=False, allow_blank=False, max_length=NAME_MAX_LEN)
    birthdate = serializers.DateField(required=True, allow_null=False)
    gender = serializers.ChoiceField(required=True, choices=GENDERS, allow_null=False, allow_blank=False)
    city = serializers.ChoiceField(required=True, choices=CITIES, allow_null=False, allow_blank=False)
    address = serializers.CharField(required=False, allow_null=True, allow_blank=False, max_length=ADDRESS_MAX_LEN)


class UserBaseSerializer(serializers.Serializer):
    _id = serializers.UUIDField(allow_null=False, read_only=True)
    username = serializers.CharField(required=True, allow_null=False, allow_blank=False, max_length=NAME_MAX_LEN)
    email = serializers.EmailField(required=True, allow_null=False, allow_blank=False)
    password = serializers.CharField(required=True, allow_null=False, allow_blank=False)
    first_name = serializers.CharField(required=True, allow_null=False, allow_blank=False, max_length=NAME_MAX_LEN)
    last_name = serializers.CharField(required=True, allow_null=False, allow_blank=False, max_length=NAME_MAX_LEN)
    birthdate = serializers.DateField(required=True, allow_null=False)
    gender = serializers.ChoiceField(required=True, choices=GENDERS, allow_null=False, allow_blank=False)
    city = serializers.ChoiceField(required=True, choices=CITIES, allow_null=False, allow_blank=False)
    address = serializers.CharField(required=False, allow_null=True, allow_blank=False, max_length=ADDRESS_MAX_LEN)
    role = serializers.ChoiceField(required=True, choices=ROLES, allow_null=False, allow_blank=False)
    authorized = serializers.BooleanField(required=True, allow_null=False)


class MatchBaseSerializer(serializers.Serializer):
    _id = serializers.UUIDField(allow_null=False, read_only=True)
    home_team = serializers.ChoiceField(required=True, choices=TEAMS, allow_null=False, allow_blank=False)
    away_team = serializers.ChoiceField(required=True, choices=TEAMS, allow_null=False, allow_blank=False)
    date = serializers.DateTimeField(required=True, allow_null=False)
    referee = serializers.CharField(required=True, allow_null=False, allow_blank=False, max_length=NAME_MAX_LEN)
    linesmen = serializers.ListField(required=True, child=serializers.CharField(allow_null=False, allow_blank=False,
                                                                                max_length=NAME_MAX_LEN), min_length=2)


class StadiumBaseSerializer(serializers.Serializer):
    _id = serializers.UUIDField(allow_null=False, required=True)
    name = serializers.CharField(allow_null=False, allow_blank=False, max_length=STADIUM_NAME_MAX_LEN, required=True)
    capacity = serializers.IntegerField(allow_null=False, required=True)
    vip_seats_per_row = serializers.IntegerField(allow_null=False, required=True)
    vip_rows = serializers.IntegerField(allow_null=False, required=True)


class SeatBaseSerializer(serializers.Serializer):
    ticket_id = serializers.UUIDField(allow_null=False, required=True)
    seat_id = serializers.CharField(required=True, allow_null=False, allow_blank=False, max_length=SEAT_ID_MAX_LEN)


class MatchSerializer(MatchBaseSerializer):
    match_venue = StadiumBaseSerializer(read_only=True)
    seats = SeatBaseSerializer(read_only=True, many=True)

    def to_representation(self, instance):
        instance.match_venue = instance.match_venue.single()
        instance.seats = instance.seats.all()
        new_representation = super().to_representation(instance)
        return new_representation


class UserSerializer(UserBaseSerializer):
    reservations = SeatBaseSerializer(read_only=True, many=True)

    def to_representation(self, instance):
        instance.reservations = instance.reservations.all()
        new_representation = super().to_representation(instance)
        return new_representation


class StadiumSerializer(StadiumBaseSerializer):
    matches = MatchBaseSerializer(read_only=True, many=True)

    def to_representation(self, instance):
        instance.matches = instance.matches.all()
        new_representation = super().to_representation(instance)
        return new_representation


class SeatSerializer(SeatBaseSerializer):
    match = MatchBaseSerializer(read_only=True)
    user = UserBaseSerializer(read_only=True)

    def to_representation(self, instance):
        instance.match = instance.match.single()
        instance.user = instance.user.single()
        new_representation = super().to_representation(instance)
        return new_representation
