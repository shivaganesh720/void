from fastapi.testclient import TestClient

def test_project_isolation_api(client: TestClient, db_session):
    # 1. Register User A
    res_a = client.post("/api/v1/auth/register", json={
        "email": "user_a@test.com", "password": "password123", "full_name": "User A"
    })
    token_a = client.post("/api/v1/auth/login", json={"email": "user_a@test.com", "password": "password123"}).json()["access_token"]
    
    # 2. Register User B
    res_b = client.post("/api/v1/auth/register", json={
        "email": "user_b@test.com", "password": "password123", "full_name": "User B"
    })
    token_b = client.post("/api/v1/auth/login", json={"email": "user_b@test.com", "password": "password123"}).json()["access_token"]
    
    # 3. User A creates a project
    res_proj = client.post("/api/v1/projects/", 
        headers={"Authorization": f"Bearer {token_a}"},
        json={"name": "Project A"}
    )
    assert res_proj.status_code == 201
    project_id = res_proj.json()["id"]
    
    # 4. User A can create a mission in their project
    res_get_a = client.post("/api/v1/missions/universal", headers={"Authorization": f"Bearer {token_a}"}, json={
        "project_id": project_id,
        "prompt": "Test"
    })
    assert res_get_a.status_code == 201
    
    # 5. User B CANNOT create a mission in User A's project
    res_get_b = client.post("/api/v1/missions/universal", headers={"Authorization": f"Bearer {token_b}"}, json={
        "project_id": project_id,
        "prompt": "Test"
    })
    assert res_get_b.status_code == 403
    assert res_get_b.json()["detail"] == "PROJECT_ACCESS_DENIED"

def test_project_not_found(client: TestClient, db_session):
    res_a = client.post("/api/v1/auth/register", json={
        "email": "user_c@test.com", "password": "password123", "full_name": "User C"
    })
    token_a = client.post("/api/v1/auth/login", json={"email": "user_c@test.com", "password": "password123"}).json()["access_token"]
    
    import uuid
    random_id = str(uuid.uuid4())
    res_get = client.post("/api/v1/missions/universal", headers={"Authorization": f"Bearer {token_a}"}, json={
        "project_id": random_id,
        "prompt": "Test"
    })
    assert res_get.status_code == 404
