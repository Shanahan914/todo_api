# To-Do API

A RESTful API for managing a user's to-do list with user registration, login, JWT authentication, CRUD operations, pagination, and filtering.

Completed as a solution to the roadmap.sh project -> https://roadmap.sh/projects/todo-list-api

## Features
- **User Registration & Login**: JWT-based authentication.
- **To-Do CRUD**: Create, read, update, and delete to-dos.
- **Pagination & Filtering**: Supports paginating and filtering to-dos.
- **Authentication**: Secure access with token authentication.
- **Validation**: Proper data validation and error handling.

## Tech Stack
- **Backend**: Python, Flask, Flask-SQLAlchemy, Flask-JWT-Extended
- **Database**: PostgreSQL (or SQLite for testing)
- **Caching**: Redis (for rate limiting)
- **Testing**: Pytest

## Endpoints
- `POST /register`: Register a new user.
- `POST /login`: Log in and receive a JWT token.
- `GET /todos`: Get a list of to-dos (pagination & filtering supported).
- `POST /todos`: Create a new to-do.
- `PUT /todos/<id>`: Update a specific to-do.
- `DELETE /todos/<id>`: Delete a to-do.

## Setup Instructions
1. Clone the repository.
2. Install dependencies: `pipenv install --dev`
3. Run the app: `flask run`
4. Run tests: `pytest`

## License
This project is open-source and available under the MIT License.
