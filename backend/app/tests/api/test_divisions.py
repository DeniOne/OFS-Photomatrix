import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app import crud
from app.schemas.division import DivisionCreate
from app.tests.utils.utils import random_string, random_lower_string
from app.tests.utils.organization import create_random_organization
from app.tests.utils.user import create_random_user, authentication_token_from_email

client = TestClient(app)

def test_create_division(db: Session) -> None:
    """Тест создания подразделения"""
    # Создаем пользователя и получаем токен
    user = create_random_user(db)
    token = authentication_token_from_email(client=client, email=user.email, db=db)
    headers = {"Authorization": f"Bearer {token}"}
    
    # Создаем организацию
    organization = create_random_organization(db)
    
    data = {
        "name": f"Test Division {random_string()}",
        "code": f"DIV_{random_lower_string(5)}",
        "description": "Test division description",
        "organization_id": organization.id,
        "is_active": True
    }
    
    response = client.post("/api/divisions/", headers=headers, json=data)
    assert response.status_code == 201
    content = response.json()
    assert content["name"] == data["name"]
    assert content["code"] == data["code"]
    assert content["organization_id"] == organization.id
    assert "id" in content
    
    # Проверяем, что подразделение действительно создано в БД
    division_id = content["id"]
    division = crud.division.get_division(db, division_id=division_id)
    assert division
    assert division.name == data["name"]

def test_read_division(db: Session) -> None:
    """Тест получения подразделения по ID"""
    # Подготовка: создаем пользователя, организацию и подразделение
    user = create_random_user(db)
    token = authentication_token_from_email(client=client, email=user.email, db=db)
    headers = {"Authorization": f"Bearer {token}"}
    
    organization = create_random_organization(db)
    
    division_data = DivisionCreate(
        name=f"Test Division {random_string()}",
        code=f"DIV_{random_lower_string(5)}",
        description="Test division description",
        organization_id=organization.id,
        is_active=True
    )
    division = crud.division.create_division(db, division_in=division_data)
    
    # Получаем подразделение по ID
    response = client.get(f"/api/divisions/{division.id}", headers=headers)
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == division.id
    assert content["name"] == division.name
    assert content["code"] == division.code
    assert content["organization_id"] == organization.id

def test_read_divisions(db: Session) -> None:
    """Тест получения списка подразделений"""
    user = create_random_user(db)
    token = authentication_token_from_email(client=client, email=user.email, db=db)
    headers = {"Authorization": f"Bearer {token}"}
    
    organization = create_random_organization(db)
    
    # Создаем несколько подразделений
    for i in range(3):
        division_data = DivisionCreate(
            name=f"Test Division {random_string()}",
            code=f"DIV_{random_lower_string(5)}",
            description=f"Test division description {i}",
            organization_id=organization.id,
            is_active=True
        )
        crud.division.create_division(db, division_in=division_data)
    
    # Получаем список всех подразделений
    response = client.get("/api/divisions/", headers=headers)
    assert response.status_code == 200
    content = response.json()
    assert len(content) >= 3  # Могут быть и другие подразделения от других тестов
    
    # Фильтруем по организации
    response = client.get(f"/api/divisions/?organization_id={organization.id}", headers=headers)
    assert response.status_code == 200
    content = response.json()
    assert len(content) == 3  # Точно 3 подразделения для этой организации

def test_update_division(db: Session) -> None:
    """Тест обновления подразделения"""
    user = create_random_user(db)
    token = authentication_token_from_email(client=client, email=user.email, db=db)
    headers = {"Authorization": f"Bearer {token}"}
    
    organization = create_random_organization(db)
    
    # Создаем подразделение
    division_data = DivisionCreate(
        name=f"Test Division {random_string()}",
        code=f"DIV_{random_lower_string(5)}",
        description="Original description",
        organization_id=organization.id,
        is_active=True
    )
    division = crud.division.create_division(db, division_in=division_data)
    
    # Обновляем подразделение
    update_data = {
        "name": f"Updated Division {random_string()}",
        "description": "Updated description"
    }
    
    response = client.put(f"/api/divisions/{division.id}", headers=headers, json=update_data)
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == division.id
    assert content["name"] == update_data["name"]
    assert content["description"] == update_data["description"]
    assert content["code"] == division.code  # Код не менялся
    
    # Проверяем, что изменения сохранились в БД
    updated_division = crud.division.get_division(db, division_id=division.id)
    assert updated_division.name == update_data["name"]
    assert updated_division.description == update_data["description"]

def test_delete_division(db: Session) -> None:
    """Тест удаления подразделения"""
    user = create_random_user(db)
    token = authentication_token_from_email(client=client, email=user.email, db=db)
    headers = {"Authorization": f"Bearer {token}"}
    
    organization = create_random_organization(db)
    
    # Создаем подразделение
    division_data = DivisionCreate(
        name=f"Test Division {random_string()}",
        code=f"DIV_{random_lower_string(5)}",
        description="Test division to delete",
        organization_id=organization.id,
        is_active=True
    )
    division = crud.division.create_division(db, division_in=division_data)
    
    # Удаляем подразделение
    response = client.delete(f"/api/divisions/{division.id}", headers=headers)
    assert response.status_code == 200
    
    # Проверяем, что подразделение удалено из БД
    deleted_division = crud.division.get_division(db, division_id=division.id)
    assert deleted_division is None

def test_create_division_with_parent(db: Session) -> None:
    """Тест создания подразделения с родительским подразделением"""
    user = create_random_user(db)
    token = authentication_token_from_email(client=client, email=user.email, db=db)
    headers = {"Authorization": f"Bearer {token}"}
    
    organization = create_random_organization(db)
    
    # Создаем родительское подразделение
    parent_data = DivisionCreate(
        name=f"Parent Division {random_string()}",
        code=f"PARENT_{random_lower_string(5)}",
        description="Parent division",
        organization_id=organization.id,
        is_active=True
    )
    parent = crud.division.create_division(db, division_in=parent_data)
    
    # Создаем дочернее подразделение
    child_data = {
        "name": f"Child Division {random_string()}",
        "code": f"CHILD_{random_lower_string(5)}",
        "description": "Child division",
        "organization_id": organization.id,
        "parent_id": parent.id,
        "is_active": True
    }
    
    response = client.post("/api/divisions/", headers=headers, json=child_data)
    assert response.status_code == 201
    content = response.json()
    assert content["parent_id"] == parent.id
    
    # Проверяем, что не удастся удалить родительское подразделение, пока есть дочернее
    response = client.delete(f"/api/divisions/{parent.id}", headers=headers)
    assert response.status_code == 400  # Bad Request 