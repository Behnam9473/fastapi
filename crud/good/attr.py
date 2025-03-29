from sqlalchemy.orm import Session
from models.good.goods import AttributeSet, Attribute, ProductAttributeValue
from schemas.good.attrs import AttributeSetCreate, AttributeCreate, ProductAttributeValueCreate
from sqlalchemy.orm import joinedload
# AttributeSet CRUD
def create_attribute_set(db: Session, attribute_set: AttributeSetCreate):
    db_attribute_set = AttributeSet(**attribute_set.dict())
    db.add(db_attribute_set)
    db.commit()
    db.refresh(db_attribute_set)
    return db_attribute_set

def get_attribute_set(db: Session, attribute_set_id: int):
    # return db.query(AttributeSet).filter(AttributeSet.id == attribute_set_id).first()
    attribute_set = db.query(AttributeSet).options(joinedload(AttributeSet.attributes)).filter(AttributeSet.id == attribute_set_id).first()
    return attribute_set
# Attribute CRUD
def create_attribute(db: Session, attribute: AttributeCreate):
    db_attribute = Attribute(**attribute.dict())
    db.add(db_attribute)
    db.commit()
    db.refresh(db_attribute)
    return db_attribute

def get_attribute(db: Session, attribute_id: int):
    return db.query(Attribute).filter(Attribute.id == attribute_id).first()

# ProductAttributeValue CRUD
def create_product_attribute_value(db: Session, product_attribute_value: ProductAttributeValueCreate):
    db_value = ProductAttributeValue(**product_attribute_value.dict())
    db.add(db_value)
    db.commit()
    db.refresh(db_value)
    return db_value

def get_product_attribute_value(db: Session, good_id: int, attribute_id: int):
    return db.query(ProductAttributeValue).filter(
        ProductAttributeValue.good_id == good_id,
        ProductAttributeValue.attribute_id == attribute_id
    ).first()

def get_all_product_attribute_values(db: Session, good_id: int):
    return db.query(ProductAttributeValue).filter(ProductAttributeValue.good_id == good_id).all()
