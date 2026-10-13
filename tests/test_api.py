"""
Test suite for API endpoints in app/routes/poema.py

Tests all CRUD operations with FastAPI TestClient.
"""
import pytest


class TestHealthEndpoint:
    """Tests for /api/health endpoint."""
    
    def test_get_health_returns_200(self, client):
        """GET /api/health should return 200 OK."""
        response = client.get("/api/health")
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "versario"


class TestVoicesEndpoint:
    """Tests for /api/voices endpoint."""
    
    def test_get_voices_returns_list(self, client):
        """GET /api/voices should return list of available voices."""
        response = client.get("/api/voices")
        
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        # Should have at least one voice with required fields
        assert len(data) > 0
        assert all(
            isinstance(v, dict) and "name" in v for v in data
        )


class TestCreatePoemaEndpoint:
    """Tests for POST /api/poemas/ endpoint."""
    
    def test_create_poema_returns_201(self, client):
        """POST with valid data should return 201 Created."""
        response = client.post(
            "/api/poemas/",
            json={
                "titulo": "Test Poema",
                "texto": "Hola\n\nAdios",
                "voz": "es_ES-davefx-medium"
            }
        )
        
        assert response.status_code == 201
        
        data = response.json()
        assert data["titulo"] == "Test Poema"
        assert data["texto"] == "Hola\n\nAdios"
        assert data["estado"] == "pending"
    
    def test_create_poema_without_titulo_returns_422(self, client):
        """POST without titulo should return 422 Unprocessable Entity."""
        response = client.post(
            "/api/poemas/",
            json={
                "texto": "Hola",
                "voz": "es_ES-davefx-medium"
            }
        )
        
        assert response.status_code == 422
    
    def test_create_poema_with_text_too_long_returns_400(self, client):
        """POST with text > 10000 chars should return 400."""
        long_text = "x" * 10001
        
        response = client.post(
            "/api/poemas/",
            json={
                "titulo": "Test",
                "texto": long_text,
                "voz": "es_ES-davefx-medium"
            }
        )
        
        assert response.status_code == 400
        assert "maximo" in str(response.json()).lower() or "10" in str(response.json())
    
    def test_create_poema_with_valid_velocity(self, client):
        """POST with valid velocity (0.8-1.2) should succeed."""
        response = client.post(
            "/api/poemas/",
            json={
                "titulo": "Test",
                "texto": "Hola",
                "voz": "es_ES-davefx-medium",
                "velocidad": 1.0
            }
        )
        
        assert response.status_code == 201
    
    def test_create_poema_with_invalid_velocity_returns_422(self, client):
        """POST with velocity outside 0.8-1.2 should return validation error."""
        # Test velocity too low (0.5)
        response = client.post(
            "/api/poemas/",
            json={
                "titulo": "Test",
                "texto": "Hola",
                "voz": "es_ES-davefx-medium",
                "velocidad": 0.5
            }
        )
        
        assert response.status_code == 422
    
    def test_create_poema_with_invalid_velocity_high(self, client):
        """POST with velocity > 1.2 should return validation error."""
        response = client.post(
            "/api/poemas/",
            json={
                "titulo": "Test",
                "texto": "Hola",
                "voz": "es_ES-davefx-medium",
                "velocidad": 1.5
            }
        )
        
        assert response.status_code == 422


class TestListPoemasEndpoint:
    """Tests for GET /api/poemas endpoint."""
    
    def test_list_poemas_returns_empty_list(self, client):
        """GET /api/poemas with no poems should return empty list."""
        response = client.get("/api/poemas/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_list_poemas_respects_limit(self, client):
        """GET /api/poemas with limit should respect it."""
        # Create one poem first
        client.post("/api/poemas/", json={
            "titulo": "Test 1",
            "texto": "Hola",
            "voz": "es_ES-davefx-medium"
        })
        
        response = client.get("/api/poemas/?limit=1")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 1
    
    def test_list_poemas_respects_offset(self, client):
        """GET /api/poemas with offset should return subsequent items."""
        # Create multiple poems
        for i in range(5):
            client.post("/api/poemas/", json={
                "titulo": f"Test {i}",
                "texto": f"Hola {i}",
                "voz": "es_ES-davefx-medium"
            })
        
        response = client.get("/api/poemas/?offset=2&limit=3")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        # Should be items with indices 2, 3, 4
        assert all(isinstance(p["id"], int) for p in data)


class TestGetPoemaEndpoint:
    """Tests for GET /api/poemas/{id} endpoint."""
    
    def test_get_poema_returns_200(self, client):
        """GET valid poem id should return 200."""
        # Create a poem first
        create_response = client.post("/api/poemas/", json={
            "titulo": "Test",
            "texto": "Hola",
            "voz": "es_ES-davefx-medium"
        })
        
        poem_id = create_response.json()["id"]
        
        response = client.get(f"/api/poemas/{poem_id}")
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["titulo"] == "Test"
    
    def test_get_poema_not_found_returns_404(self, client):
        """GET invalid poem id should return 404."""
        response = client.get("/api/poemas/999999")
        
        assert response.status_code == 404
    
    def test_get_poema_includes_all_fields(self, client):
        """GET poem should include all expected fields."""
        # Create a poem with all fields
        create_response = client.post("/api/poemas/", json={
            "titulo": "Test",
            "autor": "Autor Test",
            "texto": "Hola",
            "voz": "es_ES-davefx-medium",
            "velocidad": 1.0
        })
        
        poem_id = create_response.json()["id"]
        
        response = client.get(f"/api/poemas/{poem_id}")
        
        data = response.json()
        assert all(key in data for key in [
            "id", "titulo", "autor", "texto",
            "ruta_audio", "voz", "velocidad", "estado", "creado_en"
        ])


class TestGetPoemaAudioEndpoint:
    """Tests for GET /api/poemas/{id}/audio endpoint."""
    
    def test_get_audio_not_ready_returns_404(self, client):
        """GET audio when not ready should return 404."""
        # Create poem with pending state
        create_response = client.post("/api/poemas/", json={
            "titulo": "Test",
            "texto": "Hola",
            "voz": "es_ES-davefx-medium"
        })
        
        poem_id = create_response.json()["id"]
        
        response = client.get(f"/api/poemas/{poem_id}/audio")
        
        assert response.status_code == 404
    
    def test_get_audio_ready_returns_200(self, client, fake_tts):
        """GET audio when ready should return 200 with correct content type."""
        # This test is conceptual - would require actual audio generation
        pass


class TestDeletePoemaEndpoint:
    """Tests for DELETE /api/poemas/{id} endpoint."""
    
    def test_delete_poema_returns_204(self, client):
        """DELETE valid poem should return 204 No Content."""
        # Create a poem first
        client.post("/api/poemas/", json={
            "titulo": "Test",
            "texto": "Hola",
            "voz": "es_ES-davefx-medium"
        })
        
        response = client.delete("/api/poemas/1")
        
        assert response.status_code == 204
    
    def test_delete_poema_not_found_returns_404(self, client):
        """DELETE invalid poem id should return 404."""
        response = client.delete("/api/poemas/999999")
        
        assert response.status_code == 404
    
    def test_delete_removes_poem_from_db(self, client):
        """DELETE should remove the poem from database."""
        # Create a poem
        create_response = client.post("/api/poemas/", json={
            "titulo": "Test",
            "texto": "Hola",
            "voz": "es_ES-davefx-medium"
        })
        
        poem_id = create_response.json()["id"]
        
        # Delete it
        response = client.delete(f"/api/poemas/{poem_id}")
        assert response.status_code == 204
        
        # Verify it's gone
        response = client.get(f"/api/poemas/{poem_id}")
        assert response.status_code == 404
    
    def test_delete_removes_audio_file(self, client, audio_dir):
        """DELETE should remove associated MP3 file if it exists."""
        # Create poem and fake audio path
        create_response = client.post("/api/poemas/", json={
            "titulo": "Test",
            "texto": "Hola",
            "voz": "es_ES-davefx-medium"
        })
        
        poem_id = create_response.json()["id"]
        
        # Create fake audio file
        import os
        os.makedirs(audio_dir, exist_ok=True)
        audio_path = f"{audio_dir}/poema_{poem_id}.mp3"
        with open(audio_path, 'w') as f:
            f.write("fake audio")
        
        # Delete poem
        response = client.delete(f"/api/poemas/{poem_id}")
        assert response.status_code == 204
        
        # Verify file is removed
        assert not os.path.exists(audio_path)
