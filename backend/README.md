# OmniWhey Backend

This is the backend API for the OmniWhey homework management system.

## Project Structure

```
backend/
├── app/                # Main application package
│   ├── main.py         # FastAPI application definition
│   ├── middleware/     # Custom middleware components
│   ├── routes/         # API route handlers
│   └── utils/          # Utility functions
├── models/             # Database models
├── config/             # Configuration modules
├── alembic/            # Database migration scripts
├── tests/              # Test suite
├── run.py              # Main entry point
├── Dockerfile          # Container configuration
└── requirements.txt    # Python dependencies
```

## Running the Application

### Local Development

1. Create a virtual environment and install dependencies:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Run the application:
   ```
   python run.py
   ```
   
   Or with uvicorn directly:
   ```
   uvicorn run:app --reload
   ```

3. The API will be available at http://localhost:8000
   - Swagger UI: http://localhost:8000/api/swagger
   - ReDoc: http://localhost:8000/api/redoc

### Using Docker

1. Build and run using Docker:
   ```
   docker build -t omniwhey-backend .
   docker run -p 8000:8000 omniwhey-backend
   ```

2. Or use Docker Compose from the project root:
   ```
   docker-compose -f docker/compose.yml up
   ```

## Environment Variables

The application uses the following environment variables:

- `PORT`: Port to run the API server (default: 8000)
- `DATABASE_URL`: PostgreSQL connection string
- `JWT_SECRET_KEY`: Secret key for JWT token generation
- `JWT_ALGORITHM`: Algorithm used for JWT (default: HS256)
- `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time (default: 30)

You can set these in a `.env` file in the project root or in your environment. 