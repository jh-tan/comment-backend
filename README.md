# Comment-Backend API

A FastAPI-based comment system with GraphQL support, user authentication, and group-based permissions. This project provides both REST and GraphQL APIs for managing users, comments, and comment history with proper access controls.

## Prerequisites

Before running this project, make sure you have the following installed on your system:

- Python 3.8 or higher
- Docker and Docker Compose
- Git

## Getting Started

Follow these steps to get the project up and running:

1. Clone the repository:
```bash
git clone <repository-url>
cd comment_backend
```

2. Copy the `.env.example` file to `.env` and modify as needed:
```bash
cp .env.example .env
```
**Important Configuration Notes:**

- For Docker setup: Only modify POSTGRES_PASSWORD and POSTGRES_DB in your .env file
- Do NOT change: POSTGRES_SERVER or POSTGRES_USER when using Docker - these are fixed for current being
- For local development: Set ENVIRONMENT=local and use POSTGRES_SERVER_LOCAL and POSTGRES_USER_LOCAL variables

3. Start the application using Docker Compose:
```bash
docker-compose up --build -d
```

This command will:
- Build the Docker containers for the application and database
- Run database migrations to create all necessary tables (users, comments, comment_history)
- Seed the database with dummy data for testing
- Start the API server on port 8000
- Launch a PostgreSQL database instance

The application will be available at `http://localhost:8000` 

## API Endpoints

### Authentication Endpoints

#### POST api/v1/auth/login
Login to get access token for API authentication.

| Parameter | Type | Description |
|-----------|------|-------------|
| username | string | User's username |
| password | string | User's password |

### User Endpoints

#### POST api/v1/users/
Create a new user in the system.

| Parameter | Type | Description |
|-----------|------|-------------|
| username | string | Unique username for the user |
| password | string | Password for the user account |
| group | string | User group for permission management |

#### GET api/v1/users/
Get list of all users (requires authentication).

| Parameter | Type | Description |
|-----------|------|-------------|
| skip | integer | Number of records to skip (default: 0) |
| limit | integer | Maximum number of records to return (default: 100) |

#### GET api/v1/users/{user_id}
Get details of a specific user by ID (requires authentication).

| Parameter | Type | Description |
|-----------|------|-------------|
| user_id | integer | ID of the user to retrieve |

#### PUT api/v1/users/{user_id}
Update an existing user's information (requires authentication).

| Parameter | Type | Description |
|-----------|------|-------------|
| user_id | integer | ID of the user to update |
| username | string | New username (optional) |
| group | string | New user group (optional) |

#### DELETE api/v1/users/{user_id}
Delete a user from the system (requires authentication).

| Parameter | Type | Description |
|-----------|------|-------------|
| user_id | integer | ID of the user to delete |

### Comment Endpoints

#### POST api/v1/comments/
Create a new comment (requires authentication).

| Parameter | Type | Description |
|-----------|------|-------------|
| content | string | Content of the comment |

#### GET api/v1/comments/
Get comments from users in the same group (requires authentication).

| Parameter | Type | Description |
|-----------|------|-------------|
| skip | integer | Number of records to skip (default: 0) |
| limit | integer | Maximum number of records to return (default: 100) |

#### GET api/v1/comments/{comment_id}
Get a specific comment by ID (requires authentication and same group access).

| Parameter | Type | Description |
|-----------|------|-------------|
| comment_id | integer | ID of the comment to retrieve |

#### PUT api/v1/comments/{comment_id}
Update a comment (requires authentication and can only be done by the creator).

| Parameter | Type | Description |
|-----------|------|-------------|
| comment_id | integer | ID of the comment to update |
| content | string | New content for the comment |

#### DELETE api/v1/comments/{comment_id}
Delete a comment (requires authentication and can only be done by the creator).

| Parameter | Type | Description |
|-----------|------|-------------|
| comment_id | integer | ID of the comment to delete |

### Comment History Endpoints

#### GET api/v1/users/comment/{comment_id}
Get the edit history of a specific comment. (requires authentication and can same group access)

| Parameter | Type | Description |
|-----------|------|-------------|
| comment_id | integer | ID of the comment to get history for |
| skip | integer | Number of records to skip (default: 0) |
| limit | integer | Maximum number of records to return (default: 100) |

### Health Check

#### GET /health
Check if the API is running properly.

No parameters required.

## GraphQL API

The GraphQL endpoint is available at `/graphql` with the following operations and can only be used when authenticated:

### Queries
- `users`: Get all users
- `comments`: Get comments from the same user group
- `commentHistory(commentId: Int!)`: Get history for a specific comment

### Mutations
- `createUser(input: UserInput!)`: Create a new user
- `createComment(input: CommentInput!)`: Create a new comment
- `updateComment(commentId: Int!, input: CommentUpdateInput!)`: Update a comment

## Example API Calls

### 1. Create a user
```bash
curl -X POST "http://localhost:8000/api/v1/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "securepassword",
    "group": "developers"
  }'
```

Response:
```json
{
  "id": 1,
  "username": "john_doe",
  "group": "developers"
}
```

### 2. Login to get access token
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john_doe&password=securepassword"
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

### 3. Create a comment (authenticated)
```bash
curl -X POST "http://localhost:8000/api/v1/comments/" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "content": "This is my first comment"
  }'
```

Response:
```json
{
  "id": 1,
  "content": "This is my first comment",
  "user_id": 1,
  "created_at": "2025-08-10T10:30:00Z",
  "updated_at": null
}
```

### 4. Get comments from same group
```bash
curl -X GET "http://localhost:8000/api/v1/comments/" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

Response:
```json
[
  {
    "id": 1,
    "content": "This is my first comment",
    "user_id": 1,
    "created_at": "2025-08-10T10:30:00Z",
    "updated_at": null
  }
]
```

### 4.1 Get comments using GraphQL
```
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"query": "query { comments { id content userId createdAt updatedAt user { id username group } } }"}'
```

Response:
```json
{
  "data": {
    "comments": [
      {
        "id": 123,
        "content": "This is a comment",
        "userId": 45,
        "createdAt": "2025-08-10T12:00:00Z",
        "updatedAt": "2025-08-10T12:15:00Z",
        "user": {
          "id": 45,
          "username": "johndoe",
          "group": "admin"
        }
      }
    ]
  }
}

```

### 5. Update a comment (only creator can do this)
```bash
curl -X PUT "http://localhost:8000/api/v1/comments/1" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "content": "This is my updated comment"
  }'
```

Response:
```json
{
  "id": 1,
  "content": "This is my updated comment",
  "user_id": 1,
  "created_at": "2025-08-10T10:30:00Z",
  "updated_at": "2025-08-10T10:35:00Z"
}
```

## Forbidden Actions

The API implements strict permission controls. Here are examples of forbidden actions:

### 1. Accessing comments without authentication
```bash
curl -X GET "http://localhost:8000/api/v1/comments/"
```

Response:
```json
{
  "detail": "Not authenticated"
}
```
Status Code: 401

### 2. User from different group trying to read comments
If user "alice" (group: "managers") tries to read comments from "john_doe" (group: "developers"):

```bash
curl -X GET "http://localhost:8000/api/v1/comments/1" \
  -H "Authorization: Bearer <alice_token>"
```

Response:
```json
{
  "detail": "Not enough permissions. You can only access comments from users in your group."
}
```
Status Code: 403

### 3. Non-creator trying to update/delete comments
If user "bob" tries to update a comment created by "john_doe":

```bash
curl -X PUT "http://localhost:8000/api/v1/comments/1" \
  -H "Authorization: Bearer <bob_token>" \
  -H "Content-Type: application/json" \
  -d '{"content": "Trying to update someone else comment"}'
```

Response:
```json
{
  "detail": "Not enough permissions. You can only modify your own comments."
}
```
Status Code: 403