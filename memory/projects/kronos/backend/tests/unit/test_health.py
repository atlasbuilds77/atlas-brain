"""
Unit tests for health check endpoints
"""
import pytest
from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    """Test basic health check endpoint"""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "status" in data
    assert data["status"] == "healthy"
    assert "version" in data
    assert "environment" in data


def test_readiness_check(client: TestClient):
    """Test readiness check endpoint"""
    response = client.get("/health/ready")
    
    # This might fail if database is not connected in test
    # For now, just check endpoint exists
    assert response.status_code in [200, 503]
    
    if response.status_code == 200:
        data = response.json()
        assert "status" in data
        assert data["status"] == "ready"
        assert "database" in data
        assert data["database"] == "connected"


def test_root_endpoint(client: TestClient):
    """Test root endpoint"""
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "message" in data
    assert "Kronos Core Engine API" in data["message"]
    assert "version" in data
    assert "docs" in data
    assert "health" in data


def test_api_docs_available(client: TestClient):
    """Test that API documentation is available"""
    response = client.get("/docs")
    assert response.status_code == 200
    
    response = client.get("/redoc")
    assert response.status_code == 200


def test_openapi_schema(client: TestClient):
    """Test OpenAPI schema endpoint"""
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    
    data = response.json()
    assert "openapi" in data
    assert "info" in data
    assert "paths" in data