<br />
<p align="center">
  <a href="https://github.com/naderabdalghani/e7gzly-api">
    <img src="docs/assets/icon.png" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">E7gzly API</h3>

  <p align="center">
    A RESTful API for an Egyptian Premier League football matches ticket reservation web app
  </p>
</p>

## Table of Contents

- [About the Project](#about-the-project)
  - [Features](#features)
  - [Built With](#built-with)
  - [API Documentation](#api-documentation)

## About The Project

![Graph Schema][graph-schema]

### Features

- Clients with no authorization token can:
    - Register a new user account (as a fan or as a manager).
    - Acquire an authorization token via logging in to their existing accounts.
    - Retrieve a list of matches.
    - Retrieve a list of all stadiums.
- Clients with an unauthorized user account token can:
    - Get all his ticket reservations.
    - Cancel any of their ticket reservations.
    - Edit their profile data (except for their username and email).
    - Change their password.
- Clients with an authorized fan user account token can reserve a vacant seat for a match.
- Clients with an authorized manager user account token can:
    - Create a new match event.
    - Update the details of an existing match.
    - Add a stadium.
- Clients with an admin user account token can:
    - Authorize new users (fans and managers).
    - Get a list of users.
    - Delete a user.
- Notes:
    - The words "CLIENTS" or "CLIENT" in this document are to be interpreted as described in [RFC 2119](https://tools.ietf.org/html/rfc1856#section-2.1).
    - Requests from clients with an admin user account token are handled regardless of the account `authorized` property value.
    - The features above are listed hierarchically in a sense that a client with an authorized fan user account token can send requests that a client with an **un**authorized user account token would be able to send (e.g retrieve a list of matches).

### Built With

- [Django](https://www.djangoproject.com/)
- [Django Rest Framework](https://www.django-rest-framework.org/)
- [Neo4j](https://neo4j.com/)
- [neomodel](https://neomodel.readthedocs.io/en/latest/)
- [Swagger](https://swagger.io/)

### API Documentation

API documentation can be viewed by downloading [this directory](https://github.com/naderabdalghani/e7gzly-api/tree/master/docs) and opening index.html using a proper web browser.

[graph-schema]: docs/assets/graph.png