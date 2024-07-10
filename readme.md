# Library Management System

This is a simple library management system built using Flask, SQLAlchemy, Flask-Bcrypt, and Flask-JWT-Extended. The application allows for the management of users, books, and loans with role-based access control.

## Features

- User registration and login with role-based access (admin and client).
- CRUD operations for users, books, and loans.
- JWT-based authentication and authorization.
- Password hashing using Bcrypt.
- Role-based access control to restrict certain operations to admins only.

## Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/yourusername/library-management-system.git
    cd library-management-system
    ```

2. Create a virtual environment and activate it:

    ```sh
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. Install the required packages:

    ```sh
    pip install -r requirements.txt
    ```

4. Set up the database:

    ```sh
    flask db init
    flask db migrate
    flask db upgrade
    ```

5. Run the application:

    ```sh
    flask run
    ```

The application will be available at `http://127.0.0.1:5000`.

## API Endpoints

### Authentication

- **Login**: `POST /login`
    - Request body: 
      ```json
      {
        "username": "your_username",
        "password": "your_password"
      }
      ```
    - Response: 
      ```json
      {
        "access_token": "your_jwt_token"
      }
      ```

### User Management

- **Register**: `POST /register`
    - Request body: 
      ```json
      {
        "username": "your_username",
        "email": "your_email",
        "password": "your_password",
        "address": "your_address",
        "role": "admin|client"
      }
      ```
    - Response: 
      ```json
      {
        "id": 1,
        "username": "your_username",
        "address": "your_address",
        "role": "client",
        "email": "your_email",
        "image": null
      }
      ```

- **Get All Users** (protected): `GET /register`
    - Response: 
      ```json
      [
        {
          "id": 1,
          "username": "your_username",
          "address": "your_address",
          "role": "client",
          "email": "your_email",
          "image": null
        },
        ...
      ]
      ```

- **Get User by ID** (protected): `GET /register/<int:user_id>`
    - Response: 
      ```json
      {
        "id": 1,
        "username": "your_username",
        "address": "your_address",
        "role": "client",
        "email": "your_email",
        "image": null
      }
      ```

- **Update User** (protected, admin only): `PUT /register/<int:user_id>`
    - Request body: 
      ```json
      {
        "username": "new_username",
        "email": "new_email",
        "password": "new_password",
        "address": "new_address",
        "role": "new_role"
      }
      ```
    - Response: 
      ```json
      {
        "id": 1,
        "username": "new_username",
        "address": "new_address",
        "role": "new_role",
        "email": "new_email",
        "image": null
      }
      ```

- **Delete User** (protected, admin only): `DELETE /register/<int:user_id>`
    - Response: 
      ```json
      {
        "msg": "User deleted"
      }
      ```

### Book Management

- **Create Book** (admin only): `POST /books`
    - Request body: 
      ```json
      {
        "book_name": "book_name",
        "author": "author",
        "date_of_publish": "YYYY-MM-DD",
        "summary": "summary",
        "image": "image_url",
        "series": false
      }
      ```
    - Response: 
      ```json
      {
        "id": 1,
        "book_name": "book_name",
        "author": "author",
        "date_of_publish": "YYYY-MM-DD",
        "summary": "summary",
        "image": "image_url",
        "series": false
      }
      ```

- **Get All Books** (public): `GET /books`
    - Response: 
      ```json
      [
        {
          "id": 1,
          "book_name": "book_name",
          "author": "author",
          "date_of_publish": "YYYY-MM-DD",
          "summary": "summary",
          "image": "image_url",
          "series": false
        },
        ...
      ]
      ```

- **Get Book by ID** (public): `GET /books/<int:id>`
    - Response: 
      ```json
      {
        "id": 1,
        "book_name": "book_name",
        "author": "author",
        "date_of_publish": "YYYY-MM-DD",
        "summary": "summary",
        "image": "image_url",
        "series": false
      }
      ```

- **Update Book** (admin only): `PUT /books/<int:id>`
    - Request body: 
      ```json
      {
        "book_name": "new_book_name",
        "author": "new_author",
        "date_of_publish": "YYYY-MM-DD",
        "summary": "new_summary",
        "image": "new_image_url",
        "series": false
      }
      ```
    - Response: 
      ```json
      {
        "id": 1,
        "book_name": "new_book_name",
        "author": "new_author",
        "date_of_publish": "YYYY-MM-DD",
        "summary": "new_summary",
        "image": "new_image_url",
        "series": false
      }
      ```

- **Delete Book** (admin only): `DELETE /books/<int:id>`
    - Response: 
      ```json
      {
        "msg": "Book deleted"
      }
      ```

### Loan Management

- **Create Loan** (admin only): `POST /loans`
    - Request body: 
      ```json
      {
        "book_id": 1,
        "client_id": 2,
        "return_date": "YYYY-MM-DD"
      }
      ```
    - Response: 
      ```json
      {
        "id": 1,
        "book_name": "book_name",
        "client_name": "client_name",
        "client_address": "client_address",
        "admin_name": "admin_name",
        "admin_address": "admin_address",
        "loan_date": "YYYY-MM-DD",
        "return_date": "YYYY-MM-DD"
      }
      ```

- **Get All Loans** (protected): `GET /loans`
    - Response: 
      ```json
      [
        {
          "id": 1,
          "book_name": "book_name",
          "client_name": "client_name",
          "client_address": "client_address",
          "admin_name": "admin_name",
          "admin_address": "admin_address",
          "loan_date": "YYYY-MM-DD",
          "return_date": "YYYY-MM-DD"
        },
        ...
      ]
      ```

- **Get Loan by ID** (protected): `GET /loans/<int:id>`
    - Response: 
      ```json
      {
        "id": 1,
        "book_name": "book_name",
        "client_name": "client_name",
        "client_address": "client_address",
        "admin_name": "admin_name",
        "admin_address": "admin_address",
        "loan_date": "YYYY-MM-DD",
        "return_date": "YYYY-MM-DD"
      }
      ```

- **Delete Loan** (admin only): `DELETE /loans/<int:id>`
    - Response: 
      ```json
      {
        "msg": "Loan deleted"
      }
      ```
