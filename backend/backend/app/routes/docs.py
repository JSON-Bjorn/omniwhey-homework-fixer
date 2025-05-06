from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel

# These imports will work properly due to sys.path manipulation in run.py
from config.database import get_db
from app.auth import get_current_active_user

router = APIRouter(prefix="/api/docs", tags=["documentation"])


class EndpointDoc(BaseModel):
    path: str
    method: str
    summary: str
    description: Optional[str] = None
    requires_auth: bool = True
    requires_admin: bool = False
    query_params: Optional[List[Dict[str, str]]] = None
    path_params: Optional[List[Dict[str, str]]] = None
    request_body: Optional[Dict[str, str]] = None
    responses: Optional[Dict[str, str]] = None


class APIDocumentation(BaseModel):
    version: str
    endpoints: List[EndpointDoc]


# Get API documentation
@router.get("/", response_model=APIDocumentation)
async def get_api_documentation():
    """
    Returns documentation for all API endpoints
    """
    return {
        "version": "1.0.0",
        "endpoints": [
            # Auth endpoints
            {
                "path": "/api/login",
                "method": "POST",
                "summary": "User login",
                "description": "Authenticate a user and return a JWT token",
                "requires_auth": False,
                "requires_admin": False,
                "request_body": {
                    "email": "User's email address",
                    "password": "User's password",
                },
                "responses": {
                    "200": "Successful login, returns access token",
                    "401": "Invalid credentials",
                },
            },
            {
                "path": "/users/me",
                "method": "GET",
                "summary": "Get current user profile",
                "description": "Returns the profile of the currently authenticated user",
                "requires_auth": True,
                "requires_admin": False,
                "responses": {
                    "200": "User profile",
                    "401": "Not authenticated",
                },
            },
            # Template endpoints
            {
                "path": "/api/templates",
                "method": "GET",
                "summary": "List templates",
                "description": "Get all templates that are public or owned by the current user",
                "requires_auth": True,
                "requires_admin": False,
                "responses": {
                    "200": "List of templates",
                    "401": "Not authenticated",
                },
            },
            {
                "path": "/api/templates/{template_id}",
                "method": "GET",
                "summary": "Get template details",
                "description": "Get details of a specific template",
                "requires_auth": True,
                "requires_admin": False,
                "path_params": [
                    {
                        "name": "template_id",
                        "description": "ID of the template to retrieve",
                    },
                ],
                "responses": {
                    "200": "Template details",
                    "404": "Template not found",
                    "403": "Access denied",
                },
            },
            {
                "path": "/api/templates",
                "method": "POST",
                "summary": "Create template",
                "description": "Create a new template",
                "requires_auth": True,
                "requires_admin": False,
                "request_body": {
                    "title": "Template title",
                    "description": "Template description (optional)",
                    "structure": "JSON string containing template structure",
                    "is_public": "Boolean indicating if the template is public",
                },
                "responses": {
                    "201": "Template created",
                    "400": "Invalid input data",
                },
            },
            # Submission endpoints
            {
                "path": "/api/submissions/upload",
                "method": "POST",
                "summary": "Upload submission",
                "description": "Upload a homework submission file",
                "requires_auth": True,
                "requires_admin": False,
                "request_body": {
                    "title": "Submission title",
                    "description": "Submission description (optional)",
                    "file": "File to upload (PDF, DOCX, TXT, IPYNB)",
                },
                "responses": {
                    "201": "Submission created",
                    "400": "Invalid input or file type",
                    "401": "Not authenticated",
                },
            },
            {
                "path": "/api/submissions",
                "method": "GET",
                "summary": "List user submissions",
                "description": "Get all submissions for the current user",
                "requires_auth": True,
                "requires_admin": False,
                "query_params": [
                    {
                        "name": "status",
                        "description": "Filter by submission status (optional)",
                    },
                ],
                "responses": {
                    "200": "List of submissions",
                    "401": "Not authenticated",
                },
            },
            {
                "path": "/api/submissions/{submission_id}",
                "method": "GET",
                "summary": "Get submission details",
                "description": "Get details of a specific submission",
                "requires_auth": True,
                "requires_admin": False,
                "path_params": [
                    {
                        "name": "submission_id",
                        "description": "ID of the submission to retrieve",
                    },
                ],
                "responses": {
                    "200": "Submission details",
                    "404": "Submission not found",
                    "403": "Access denied",
                },
            },
            # Feedback endpoints
            {
                "path": "/api/feedback/{submission_id}",
                "method": "GET",
                "summary": "Get feedback",
                "description": "Get feedback for a specific submission",
                "requires_auth": True,
                "requires_admin": False,
                "path_params": [
                    {
                        "name": "submission_id",
                        "description": "ID of the submission",
                    },
                ],
                "responses": {
                    "200": "Feedback details",
                    "404": "Submission or feedback not found",
                    "403": "Access denied",
                },
            },
            {
                "path": "/api/feedback/list",
                "method": "GET",
                "summary": "List user feedback",
                "description": "Get all feedback for the current user's submissions",
                "requires_auth": True,
                "requires_admin": False,
                "responses": {
                    "200": "List of feedback",
                    "401": "Not authenticated",
                },
            },
            # Admin endpoints
            {
                "path": "/api/admin/users",
                "method": "GET",
                "summary": "List all users",
                "description": "Admin only: Get paginated list of all users",
                "requires_auth": True,
                "requires_admin": True,
                "query_params": [
                    {
                        "name": "page",
                        "description": "Page number (default: 1)",
                    },
                    {
                        "name": "per_page",
                        "description": "Items per page (default: 10)",
                    },
                    {
                        "name": "search",
                        "description": "Filter by email (optional)",
                    },
                ],
                "responses": {
                    "200": "List of users with pagination data",
                    "401": "Not authenticated",
                    "403": "Not an admin",
                },
            },
            {
                "path": "/api/admin/submissions",
                "method": "GET",
                "summary": "List all submissions",
                "description": "Admin only: Get paginated list of all submissions",
                "requires_auth": True,
                "requires_admin": True,
                "query_params": [
                    {
                        "name": "page",
                        "description": "Page number (default: 1)",
                    },
                    {
                        "name": "per_page",
                        "description": "Items per page (default: 10)",
                    },
                    {
                        "name": "status",
                        "description": "Filter by status (optional)",
                    },
                    {
                        "name": "user_id",
                        "description": "Filter by user ID (optional)",
                    },
                ],
                "responses": {
                    "200": "List of submissions with pagination data",
                    "401": "Not authenticated",
                    "403": "Not an admin",
                },
            },
        ],
    }
