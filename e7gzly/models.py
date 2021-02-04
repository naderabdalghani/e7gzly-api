# python .\venv\Scripts\neomodel_install_labels manage.py e7gzly.models --db bolt://neo4j:0123456789@localhost:7687
# python .\venv\Scripts\neomodel_remove_labels --db bolt://neo4j:0123456789@localhost:7687
import binascii
import os
import re

from neomodel import StructuredNode, StringProperty, EmailProperty, DateTimeProperty, DateProperty, IntegerProperty, \
    ArrayProperty, RelationshipTo, One, ZeroOrOne, UniqueIdProperty, RelationshipFrom, BooleanProperty
from .constants import NAME_MAX_LEN, STADIUM_NAME_MAX_LEN, CITIES, GENDERS, TEAMS, ROLES, SEAT_ID_MAX_LEN, \
    ADDRESS_MAX_LEN, TOKEN_MAX_LEN
from .utilities import row_to_number


class Seat(StructuredNode):
    ticket_id = UniqueIdProperty()
    seat_id = StringProperty(required=True, max_length=SEAT_ID_MAX_LEN)
    match = RelationshipTo('Match', 'FOR', cardinality=One)
    user = RelationshipFrom('User', 'RESERVED_A', cardinality=One)


class User(StructuredNode):
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
    token = RelationshipTo('Token', 'BEARS_A', cardinality=ZeroOrOne)


class Stadium(StructuredNode):
    stadium_id = UniqueIdProperty()
    name = StringProperty(required=True, max_length=STADIUM_NAME_MAX_LEN, unique_index=True)
    capacity = IntegerProperty(required=True)
    vip_seats_per_row = IntegerProperty(required=True)
    vip_rows = IntegerProperty(required=True)
    matches = RelationshipFrom("Match", "HOSTED_IN")

    def is_valid_seat(self, seat_id):
        seat_id = seat_id.upper()
        try:
            string_match_object = re.match("^([A-Z]+)([0-9]+)$", seat_id)
            row = string_match_object.group(1)
            seat = string_match_object.group(2)
            if row_to_number(row) >= self.vip_rows or int(seat) >= self.vip_seats_per_row:
                return False
        except (AttributeError, IndexError):
            return False
        return True


class Match(StructuredNode):
    match_id = UniqueIdProperty()
    home_team = StringProperty(required=True, choices=TEAMS)
    away_team = StringProperty(required=True, choices=TEAMS)
    date = DateTimeProperty(required=True)
    referee = StringProperty(required=True, max_length=NAME_MAX_LEN)
    linesmen = ArrayProperty(StringProperty(max_length=NAME_MAX_LEN), required=True)
    match_venue = RelationshipTo('Stadium', 'HOSTED_IN', cardinality=One)
    seats = RelationshipFrom("Seat", "FOR")

    def is_available_seat(self, seat_id):
        reserved_seat = self.seats.filter(seat_id=seat_id)
        if reserved_seat is None:
            return True
        return False


class Token(StructuredNode):
    key = StringProperty(max_length=TOKEN_MAX_LEN, unique_index=True)
    created = DateTimeProperty(default_now=True)
    user = RelationshipFrom('User', 'BEARS_A', cardinality=One)

    def __init__(self, *args, **kwargs):
        kwargs["key"] = self.generate_key()
        super().__init__(*args, **kwargs)

    @classmethod
    def generate_key(cls):
        return binascii.hexlify(os.urandom(20)).decode()

    def __str__(self):
        return self.key
