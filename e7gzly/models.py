import binascii
import os
from neomodel import StructuredNode, StringProperty, EmailProperty, DateTimeProperty, DateProperty, IntegerProperty, \
    ArrayProperty, RelationshipTo, One, ZeroOrOne, UniqueIdProperty, RelationshipFrom, BooleanProperty
from .constants import NAME_MAX_LEN, STADIUM_NAME_MAX_LEN, CITIES, GENDERS, TEAMS, ROLES, SEAT_ID_MAX_LEN, \
    ADDRESS_MAX_LEN, TOKEN_MAX_LEN


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
    token = RelationshipTo('Token', 'BEARS_A', cardinality=ZeroOrOne)

    def update(self, data):
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.birthdate = data['birthdate']
        self.gender = data['gender']
        self.city = data['city']
        self.address = data.get('address', None)
        if hasattr(self, 'deleted') and self.deleted:
            raise ValueError("{0}.save() attempted on deleted node".format(self.__class__.__name__))
        if hasattr(self, 'id'):
            params = self.deflate(self.__properties__, self)
            params.pop('_id')
            query = "MATCH (n) WHERE id(n)=$self \n"
            query += "\n".join(["SET n.{0} = ${1}".format(key, key) + "\n" for key in params.keys()])
            for label in self.inherited_labels():
                query += "SET n:`{0}`\n".format(label)
            self.cypher(query, params)
        return self


class Stadium(StructuredNode):
    _id = UniqueIdProperty()
    name = StringProperty(required=True, max_length=STADIUM_NAME_MAX_LEN, unique_index=True)
    capacity = IntegerProperty(required=True)
    vip_seats_per_row = IntegerProperty(required=True)
    vip_rows = IntegerProperty(required=True)
    matches = RelationshipFrom("Match", "HOSTED_IN")

    def is_valid_seat(self, seat_id):
        return True


class Match(StructuredNode):
    _id = UniqueIdProperty()
    home_team = StringProperty(required=True, choices=TEAMS)
    away_team = StringProperty(required=True, choices=TEAMS)
    date = DateTimeProperty(required=True)
    referee = StringProperty(required=True, max_length=NAME_MAX_LEN)
    linesmen = ArrayProperty(StringProperty(max_length=NAME_MAX_LEN), required=True)
    match_venue = RelationshipTo('Stadium', 'HOSTED_IN', cardinality=One)
    seats = RelationshipFrom("Seat", "FOR")

    def update(self, data):
        self.home_team = data['home_team']
        self.away_team = data['away_team']
        self.date = data['date']
        self.referee = data['referee']
        self.linesmen = data['linesmen']
        if hasattr(self, 'deleted') and self.deleted:
            raise ValueError("{0}.save() attempted on deleted node".format(self.__class__.__name__))
        if hasattr(self, 'id'):
            params = self.deflate(self.__properties__, self)
            params.pop('_id')
            query = "MATCH (n) WHERE id(n)=$self \n"
            query += "\n".join(["SET n.{0} = ${1}".format(key, key) + "\n" for key in params.keys()])
            for label in self.inherited_labels():
                query += "SET n:`{0}`\n".format(label)
            self.cypher(query, params)
        return self

    def is_available_seat(self, seat_id):
        reserved_seats = self.seats.all()
        for seat in reserved_seats:
            if seat_id == seat.seat_id:
                return False
        return True


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
