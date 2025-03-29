import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.good.colors import Color, Base
from schemas.good.colors import ColorCreate, ColorUpdate
from crud.good.colors import color as color_crud

SQLALCHEMY_DATABASE_URL = "sqlite:///./test1.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)




def test_create_color(db: Session):
    color_in = ColorCreate(name="Red", code="#FF0000")
    color = color_crud.create(db=db, obj_in=color_in)
    assert color.name == "Red"
    assert color.code == "#FF0000"

def test_create_duplicate_color(db: Session):
    color_in = ColorCreate(name="Blue", code="#0000FF")
    color_crud.create(db=db, obj_in=color_in)
    
    # Try creating duplicate
    with pytest.raises(Exception):
        color_crud.create(db=db, obj_in=color_in)

def test_get_color(db: Session):
    color_in = ColorCreate(name="Green", code="#00FF00")
    created_color = color_crud.create(db=db, obj_in=color_in)
    
    color = color_crud.get(db=db, id=created_color.id)
    assert color.name == "Green"
    assert color.code == "#00FF00"

def test_get_nonexistent_color(db: Session):
    color = color_crud.get(db=db, id=999)
    assert color is None

def test_get_colors(db: Session):
    color_in1 = ColorCreate(name="Yellow", code="#FFFF00")
    color_in2 = ColorCreate(name="Purple", code="#800080")
    
    color_crud.create(db=db, obj_in=color_in1)
    color_crud.create(db=db, obj_in=color_in2)
    
    colors = color_crud.get_multi(db=db)
    assert len(colors) >= 2

def test_update_color(db: Session):
    color_in = ColorCreate(name="Orange", code="#FFA500")
    color = color_crud.create(db=db, obj_in=color_in)
    
    update_data = ColorUpdate(name="Dark Orange", code="#FF8C00")
    updated_color = color_crud.update(db=db, id=color.id, obj_in=update_data)
    
    assert updated_color.name == "Dark Orange"
    assert updated_color.code == "#FF8C00"

def test_delete_color(db: Session):
    color_in = ColorCreate(name="Brown", code="#A52A2A")
    color = color_crud.create(db=db, obj_in=color_in)
    
    deleted_color = color_crud.delete(db=db, id=color.id)
    assert deleted_color.id == color.id
    
    # Verify deletion
    assert color_crud.get(db=db, id=color.id) is None