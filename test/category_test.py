import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session
import sys
import os
from schemas.good.category import CategoryCreate, CategoryUpdate
from routers.good.category import create_category, get_categories, update_category, delete_category
from models.good.goods import Category

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def test_category_data():
    return {
        "name": "Test Category"
    }

@pytest.fixture
def test_db(mocker):
    # Mock DB session
    db = mocker.Mock(spec=Session)
    return db

def test_create_category(test_db, test_category_data):
    category_data = CategoryCreate(**test_category_data)
    
    # Mock DB query for existing categories
    mock_query = test_db.query.return_value
    mock_query.offset.return_value.limit.return_value.all.return_value = []
    
    # Mock category creation
    new_category = Category(**test_category_data)
    new_category.id = 1
    test_db.add.return_value = None
    test_db.commit.return_value = None
    test_db.refresh.return_value = None
    
    result = create_category(category_data, test_db)
    
    assert result.name == test_category_data["name"]
    test_db.add.assert_called_once()
    test_db.commit.assert_called_once()

    
def test_create_duplicate_category(test_db, test_category_data):
    category_data = CategoryCreate(**test_category_data)
    
    # Mock existing category
    existing_categories = [Category(**test_category_data)]
    test_db.query.return_value.offset.return_value.limit.return_value.all.return_value = existing_categories
    
    with pytest.raises(HTTPException) as exc_info:
        create_category(category_data, test_db)
    
    assert exc_info.value.status_code == 400
    assert "Category with this name already exists" in str(exc_info.value.detail)

def test_get_categories(test_db):
    # Mock categories list
    mock_categories = [
        Category(id=1, name="Category 1"),
        Category(id=2, name="Category 2")
    ]
    test_db.query.return_value.offset.return_value.limit.return_value.all.return_value = mock_categories
    
    result = get_categories(test_db)
    
    assert len(mock_categories) == 2
    assert mock_categories[0].name == "Category 1"
    assert mock_categories[1].name == "Category 2"

def test_update_category(test_db):
    category_id = 1
    update_data = CategoryUpdate(name="Updated Category")
    
    # Mock existing category
    existing_category = Category(id=category_id, name="Old Name")
    test_db.query.return_value.filter.return_value.first.return_value = existing_category
    
    result = update_category(category_id, update_data, test_db)
    
    assert result.name == "Updated Category"
    test_db.commit.assert_called_once()

def test_update_nonexistent_category(test_db):
    category_id = 999
    update_data = CategoryUpdate(name="Updated Category")
    
    # Mock no existing category
    test_db.query.return_value.filter.return_value.first.return_value = None
    
    with pytest.raises(HTTPException) as exc_info:
        update_category(category_id, update_data, test_db)
    
    assert exc_info.value.status_code == 404
    assert "Category not found" in str(exc_info.value.detail)

def test_delete_category(test_db):
    category_id = 1
    
    # Mock existing category
    existing_category = Category(id=category_id, name="Test Category")
    test_db.query.return_value.filter.return_value.first.return_value = existing_category
    
    result = delete_category(category_id, test_db)
    
    assert result.id == category_id
    test_db.delete.assert_called_once()
    test_db.commit.assert_called_once()

def test_delete_nonexistent_category(test_db):
    category_id = 999
    
    # Mock no existing category
    test_db.query.return_value.filter.return_value.first.return_value = None
    
    with pytest.raises(HTTPException) as exc_info:
        delete_category(category_id, test_db)
    
    assert exc_info.value.status_code == 404
    assert "Category not found" in str(exc_info.value.detail)