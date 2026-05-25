from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

# Существующие пользователи (из fake_db)
users = [
    {
        'id': 1,
        'name': 'Ivan Ivanov',
        'email': 'i.i.ivanov@mail.com',
    },
    {
        'id': 2,
        'name': 'Petr Petrov',
        'email': 'p.p.petrov@mail.com',
    }
]


def test_get_existed_user():
    '''Получение существующего пользователя'''
    response = client.get("/api/v1/user", params={'email': users[0]['email']})
    assert response.status_code == 200
    assert response.json()['id'] == users[0]['id']
    assert response.json()['name'] == users[0]['name']
    assert response.json()['email'] == users[0]['email']


def test_get_unexisted_user():
    '''Получение несуществующего пользователя'''
    response = client.get("/api/v1/user", params={'email': 'nonexistent@example.com'})
    assert response.status_code == 404
    assert response.json()['detail'] == "User not found"


def test_create_user_with_valid_email():
    '''Создание пользователя с уникальной почтой'''
    new_user = {
        'name': 'Sidor Sidorov',
        'email': 'sidor@example.com'
    }
    response = client.post("/api/v1/user", json=new_user)
    assert response.status_code == 201
    # ВНИМАНИЕ: POST возвращает ID (число), а не объект пользователя!
    user_id = response.json()
    assert isinstance(user_id, int)

    # Проверяем, что пользователь действительно создался
    get_response = client.get("/api/v1/user", params={'email': new_user['email']})
    assert get_response.status_code == 200
    assert get_response.json()['name'] == new_user['name']
    assert get_response.json()['email'] == new_user['email']


def test_create_user_with_invalid_email():
    '''Создание пользователя с почтой, которую использует другой пользователь'''
    duplicate_user = {
        'name': 'Duplicate Name',
        'email': users[0]['email']  # email уже существует
    }
    response = client.post("/api/v1/user", json=duplicate_user)
    assert response.status_code == 409
    assert response.json()['detail'] == "User with this email already exists"


def test_delete_user():
    '''Удаление пользователя'''
    # Сначала создаём пользователя для удаления
    new_user = {
        'name': 'To Delete',
        'email': 'todelete@example.com'
    }
    create_response = client.post("/api/v1/user", json=new_user)
    assert create_response.status_code == 201

    # Удаляем пользователя по email
    delete_response = client.delete("/api/v1/user", params={'email': new_user['email']})
    assert delete_response.status_code == 204
    assert delete_response.text == ''  # Нет тела ответа

    # Проверяем, что пользователь действительно удалён
    get_response = client.get("/api/v1/user", params={'email': new_user['email']})
    assert get_response.status_code == 404