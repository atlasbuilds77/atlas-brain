"""
Quick test suite for Kronos Core Engine
Run with: pytest tests/test_main.py
"""

import pytest
from httpx import AsyncClient
from main import app


@pytest.mark.asyncio
async def test_root():
    """Test root endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Kronos Core Engine API"
        assert "version" in data


@pytest.mark.asyncio
async def test_health():
    """Test health check"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_register_user():
    """Test user registration"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "name": "Test User",
                "password": "testpass123",
                "role": "client"
            }
        )
        assert response.status_code in [201, 400]  # 400 if user exists


@pytest.mark.asyncio
async def test_login_invalid():
    """Test login with invalid credentials"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_leads_unauthorized():
    """Test leads endpoint without authentication"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/leads")
        assert response.status_code == 403  # Forbidden without auth


@pytest.mark.asyncio
async def test_openapi_spec():
    """Test OpenAPI specification is available"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/openapi.json")
        assert response.status_code == 200
        spec = response.json()
        assert "openapi" in spec
        assert "paths" in spec
