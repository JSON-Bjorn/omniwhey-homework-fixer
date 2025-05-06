# Omniwhey Homework Fixer Backend

A FastAPI backend for an AI-powered assignment correction system.

## Features

- Assignment upload and management for teachers
- Assignment submission and scoring for students
- AI-powered grading using OpenAI and Anthropic APIs
- Token-based authentication for teachers and students
- Role-based access control

## Tech Stack

- Python 3.12
- FastAPI
- SQLAlchemy 2.0 with asyncpg
- Pydantic v2
- OpenAI and Anthropic APIs
- PostgreSQL

## Project Structure

```
app/
├── ai/                  # AI integration services
├── api/                 # API endpoints
│   └── routers/         # API routers for different entities
├── core/                # Core application modules
├── crud/                # Database CRUD operations
├── db/                  # Database models and connections
├── models/              # SQLAlchemy models
├── schemas/             # Pydantic schemas
├── services/            # Business logic services
├── utils/               # Utility functions
└── main.py              # Application entry point
```

## Setup & Running

### Prerequisites

- Python 3.12+
- PostgreSQL
- Redis (optional, for rate limiting)

### Environment Setup

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment: 
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and fill in the required values

### Database Setup

1. Create a PostgreSQL database
2. Update the `.env` file with the database connection details

### Running the Application

```bash
# Development mode
uvicorn app.main:app --reload

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### API Documentation

- Swagger UI: `/docs`
- ReDoc: `/redoc`

## Authentication

The API uses JWT tokens for authentication. To access protected endpoints:

1. Register a user (student or teacher)
2. Login to get an access token
3. Include the token in the `Authorization` header as `Bearer {token}`

## License

This project is licensed under the MIT License - see the LICENSE file for details. 