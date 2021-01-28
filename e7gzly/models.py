import datetime
from neomodel import StructuredNode, StringProperty, EmailProperty, DateTimeProperty, DateProperty, IntegerProperty, \
    ArrayProperty, RelationshipTo, One, UniqueIdProperty, RelationshipFrom, BooleanProperty
from rest_framework.exceptions import ValidationError
from .constants import NAME_MAX_LEN, STADIUM_NAME_MAX_LEN, CITIES, GENDERS, TEAMS, ROLES, SEAT_ID_MAX_LEN, \
    STADIUM_MIN_CAPACITY, VIP_SEATS_PER_ROW_MIN, VIP_ROWS_MIN, VIP_ROWS_MAX, VIP_SEATS_PER_ROW_MAX, ADDRESS_MAX_LEN


class Admin(StructuredNode):
    _id = UniqueIdProperty()
    username = StringProperty(required=True, max_length=NAME_MAX_LEN, unique_index=True)
    email = EmailProperty(required=True, unique_index=True)
    password = StringProperty(required=True)
    first_name = StringProperty(required=True)
    last_name = StringProperty(required=True)
    birthdate = DateProperty(required=True)
    gender = StringProperty(required=True, choices=GENDERS)
    city = StringProperty(required=True, choices=CITIES)
    address = StringProperty(required=False)


class Seat(StructuredNode):
    ticket_id = UniqueIdProperty()
    seat_id = StringProperty(required=True, max_length=SEAT_ID_MAX_LEN)
    match = RelationshipTo('Match', 'FOR', cardinality=One)
    user = RelationshipFrom('User', 'RESERVED_A', cardinality=One)


class User(StructuredNode):
    _id = UniqueIdProperty()
    username = StringProperty(required=True, max_length=NAME_MAX_LEN, unique_index=True)
    email = EmailProperty(required=True, unique_index=True)
    password = StringProperty(required=True)
    first_name = StringProperty(required=True, max_length=NAME_MAX_LEN)
    last_name = StringProperty(required=True, max_length=NAME_MAX_LEN)
    birthdate = DateProperty(required=True)
    gender = StringProperty(required=True, choices=GENDERS)
    city = StringProperty(required=True, choices=CITIES)
    address = StringProperty(required=False, max_length=ADDRESS_MAX_LEN)
    role = StringProperty(required=True, choices=ROLES)
    authorized = BooleanProperty(default=False)
    reservations = RelationshipTo('Seat', 'RESERVED_A')


class Stadium(StructuredNode):
    _id = UniqueIdProperty()
    name = StringProperty(required=True, max_length=STADIUM_NAME_MAX_LEN, unique_index=True)
    capacity = IntegerProperty(required=True)
    vip_seats_per_row = IntegerProperty(required=True)
    vip_rows = IntegerProperty(required=True)
    matches = RelationshipFrom("Match", "HOSTED_IN")


class Match(StructuredNode):
    _id = UniqueIdProperty()
    home_team = StringProperty(required=True, choices=TEAMS)
    away_team = StringProperty(required=True, choices=TEAMS)
    date = DateTimeProperty(required=True)
    referee = StringProperty(required=True, max_length=NAME_MAX_LEN)
    linesmen = ArrayProperty(StringProperty(max_length=NAME_MAX_LEN), required=True)
    match_venue = RelationshipTo('Stadium', 'HOSTED_IN', cardinality=One)
    seats = RelationshipFrom("Seat", "FOR")
