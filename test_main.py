import pytest
from fastapi.testclient import TestClient
from main import app
from database import driver

client = TestClient(app)

TEST_USER = {
    "id": 1,
    "name": "Test User",
    "screen_name": "testuser",
    "sex": "M",
    "home_town": "Test Town"
}

# Функция для подготовки данных перед тестами
def setup_test_data():
    with driver.session() as session:
        # Создаем тестового пользователя
        session.run("""
            MERGE (u:User {id: $id})
            SET u.name = $name, u.screen_name = $screen_name,
                u.sex = $sex, u.home_town = $home_town
        """, **TEST_USER)

# Функция для очистки тестовых данных
def teardown_test_data():
    with driver.session() as session:
        session.run("MATCH (n:User) DETACH DELETE n")

# Pytest для настройки данных
@pytest.fixture(autouse=True)
def prepare_database():
    setup_test_data()
    yield
    teardown_test_data()

# Тесты
def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Neo4j FastAPI Service is running"}

def test_get_all_nodes():
    response = client.get("/nodes/")
    assert response.status_code == 200
    assert "nodes" in response.json()

# Тест добавления узла
def test_add_node():
    new_user = {
        "id": 2,
        "name": "New User",
        "screen_name": "newuser",
        "sex": 1,
        "home_town": "New Town"
    }
    headers = {"Authorization": "Bearer SUPERAUTHTOKEN"}
    response = client.post("/nodes/", json=new_user, headers=headers)
    assert response.status_code == 200
    assert response.json() == {"message": "User 2 created"}

# Тест получения узла с его связями
def test_get_node_with_relationships():
    new_user = {
        "id": 2,
        "name": "New User",
        "screen_name": "newuser",
        "sex": 1,
        "home_town": "Test Town"
    }
    with driver.session() as session:
        session.run("""
            MERGE (u:User {id: $id})
            SET u.name = $name, u.screen_name = $screen_name,
                u.sex = $sex, u.home_town = $home_town
        """, **new_user)

    response = client.get("/nodes/2")
    assert response.status_code == 200
    data = response.json()

    assert "node" in data
    assert "follows" in data
    assert "subscribes" in data
    assert data["node"]["id"] == 2


def test_add_node_without_token():
    new_user = {
        "id": 2,
        "name": "New User",
        "screen_name": "newuser",
        "sex": 1,
        "home_town": "New Town"
    }
    response = client.post("/nodes/", json=new_user)
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token"}

def test_delete_node():
    headers = {"Authorization": "Bearer SUPERAUTHTOKEN"}
    response = client.delete(f"/nodes/{TEST_USER['id']}", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"message": f"User {TEST_USER['id']} deleted"}

def test_delete_node_without_token():
    response = client.delete(f"/nodes/{TEST_USER['id']}")
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token"}

def test_get_node_not_found():
    response = client.get("/nodes/9999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Node not found"}
