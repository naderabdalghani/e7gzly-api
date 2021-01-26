from neomodel import StructuredNode, StringProperty, EmailProperty, DateTimeProperty, DateProperty, IntegerProperty, \
    ArrayProperty, RelationshipTo, One, UniqueIdProperty, RelationshipFrom

USERNAME_LEN = 50
STADIUM_NAME_LEN = 100

GENDERS = (
    ('male', 'Male'),
    ('female', 'Female'),
    ('other', 'Other')
)

ROLES = (
    ('manager', 'Manager'),
    ('fan', 'Fan')
)

TEAMS = (
    ('al ahly sc', 'Al Ahly SC'),
    ('zamalek sc', 'Zamalek SC'),
    ('el gouna fc', 'El Gouna FC'),
    ('al masry sc', 'Al Masry SC'),
    ('pyramids fc', 'Pyramids FC'),
    ('enppi sc', 'ENPPI SC'),
    ('misr lel makkasa sc', 'Misr Lel Makkasa SC'),
    ('ceramica cleopatra fc', 'Ceramica Cleopatra FC'),
    ('smouha sc', 'Smouha SC'),
    ('national bank of egypt sc', 'National Bank of Egypt SC'),
    ('ghazl el mahalla sc', 'Ghazl El Mahalla SC'),
    ('al ittihad alexandria club', 'Al Ittihad Alexandria Club'),
    ('aswan sc', 'Aswan SC'),
    ('ismaily sc', 'Ismaily SC'),
    ("tala'ea el gaish sc", "Tala'ea El Gaish SC"),
    ('al mokawloon al arab sc', 'Al Mokawloon Al Arab SC'),
    ('wadi degla sc', 'Wadi Degla SC'),
    ('el entag el harby sc', 'El Entag El Harby SC')
)


class Admin(StructuredNode):
    username = StringProperty(required=True, max_length=USERNAME_LEN, unique_index=True)
    email = EmailProperty(required=True, unique_index=True)
    password = StringProperty(required=True)
    first_name = StringProperty(required=True)
    last_name = StringProperty(required=True)
    birthdate = DateProperty(required=True)
    gender = StringProperty(required=True, choices=GENDERS)
    city = StringProperty(required=True)
    address = StringProperty(required=False)


class Seat(StructuredNode):
    ticket_id = UniqueIdProperty()
    seat_id = StringProperty(required=True)
    match = RelationshipTo('Match', 'FOR', cardinality=One)
    user = RelationshipFrom('User', 'RESERVED_A', cardinality=One)


class User(StructuredNode):
    username = StringProperty(required=True, max_length=USERNAME_LEN, unique_index=True)
    email = EmailProperty(required=True, unique_index=True)
    password = StringProperty(required=True)
    first_name = StringProperty(required=True)
    last_name = StringProperty(required=True)
    birthdate = DateProperty(required=True)
    gender = StringProperty(required=True, choices=GENDERS)
    city = StringProperty(required=True)
    address = StringProperty(required=False)
    role = StringProperty(required=True, choices=ROLES)
    reservations = RelationshipTo('Seat', 'RESERVED_A')


class Stadium(StructuredNode):
    name = StringProperty(required=True, max_length=STADIUM_NAME_LEN, unique_index=True)
    seats = IntegerProperty(required=True)
    vip_seats_per_row = IntegerProperty(required=True)
    vip_rows = IntegerProperty(required=True)


class Match(StructuredNode):
    home_team = StringProperty(required=True, choices=TEAMS)
    away_team = EmailProperty(required=True, choices=TEAMS)
    date = DateTimeProperty(required=True)
    referee = StringProperty(required=True)
    linesmen = ArrayProperty(StringProperty(), required=True)
    match_venue = RelationshipTo('Stadium', 'HOSTED_IN', cardinality=One)
    seats = RelationshipFrom("Seat", "FOR")
