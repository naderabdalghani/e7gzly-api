import datetime

from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .constants import NAME_MAX_LEN, STADIUM_NAME_MAX_LEN, CITIES, GENDERS, TEAMS, ROLES, \
    SEAT_ID_MAX_LEN, ADDRESS_MAX_LEN, STADIUM_MIN_CAPACITY, VIP_SEATS_PER_ROW_MIN, VIP_ROWS_MIN, \
    VIP_SEATS_PER_ROW_MAX, VIP_ROWS_MAX, DATETIME_FORMAT, MAX_BIRTHDATE, MIN_AGE


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
    authorized = serializers.BooleanField(allow_null=False, read_only=True)

    def validate(self, data):
        if data['role'] == 'admin':
            raise ValidationError({"role": "Cannot create a user with the given role"})
        if data['birthdate'] > MAX_BIRTHDATE:
            raise ValidationError({"birthdate": "User must be at least {} years old to register an account"
                                   .format(MIN_AGE)})
        return data


class MatchBaseSerializer(serializers.Serializer):
    _id = serializers.UUIDField(allow_null=False, read_only=True)
    home_team = serializers.ChoiceField(required=True, choices=TEAMS, allow_null=False, allow_blank=False)
    away_team = serializers.ChoiceField(required=True, choices=TEAMS, allow_null=False, allow_blank=False)
    date = serializers.DateTimeField(required=True, allow_null=False)
    referee = serializers.CharField(required=True, allow_null=False, allow_blank=False, max_length=NAME_MAX_LEN)
    linesmen = serializers.ListField(required=True, child=serializers.CharField(allow_null=False, allow_blank=False,
                                                                                max_length=NAME_MAX_LEN), min_length=2)

    def validate(self, data):
        if not isinstance(data['date'], datetime.datetime):
            data['date'] = datetime.datetime.strptime(data['date'], DATETIME_FORMAT)
        if data['home_team'] == data['away_team']:
            raise ValidationError({"away_team": "Away team cannot be the same as the home team"})
        if data['date'] < timezone.now():
            raise ValidationError({"date": "Only future match events are allowed to be added"})
        if len(data['linesmen']) < 2:
            raise ValidationError({"linesmen": "There should be at least 2 linesmen for a single match"})
        return data


class StadiumBaseSerializer(serializers.Serializer):
    _id = serializers.UUIDField(allow_null=False, required=True)
    name = serializers.CharField(allow_null=False, allow_blank=False, max_length=STADIUM_NAME_MAX_LEN, required=True)
    capacity = serializers.IntegerField(allow_null=False, required=True)
    vip_seats_per_row = serializers.IntegerField(allow_null=False, required=True)
    vip_rows = serializers.IntegerField(allow_null=False, required=True)

    def validate(self, data):
        if data['capacity'] < STADIUM_MIN_CAPACITY:
            raise ValidationError({"capacity": "Invalid stadium capacity (less than {})".format(STADIUM_MIN_CAPACITY)})
        if data['vip_seats_per_row'] < VIP_SEATS_PER_ROW_MIN:
            raise ValidationError({"vip_seats_per_row": "Invalid number of VIP seats per row (less than {})"
                                  .format(VIP_SEATS_PER_ROW_MIN)})
        if data['vip_rows'] < VIP_ROWS_MIN:
            raise ValidationError({"vip_rows": "Invalid number of VIP rows (less than {})"
                                  .format(VIP_ROWS_MIN)})
        if data['vip_seats_per_row'] > VIP_SEATS_PER_ROW_MAX:
            raise ValidationError({"vip_seats_per_row": "Invalid number of VIP seats per row (more than {})"
                                  .format(VIP_SEATS_PER_ROW_MAX)})
        if data['vip_rows'] > VIP_ROWS_MAX:
            raise ValidationError({"vip_rows": "Invalid number of VIP rows (more than {})"
                                  .format(VIP_ROWS_MAX)})
        return data


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


class LoginDataSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, allow_null=False, allow_blank=False)
    password = serializers.CharField(required=True, allow_null=False, allow_blank=False)
