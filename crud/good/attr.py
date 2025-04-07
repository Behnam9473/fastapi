from sqlalchemy.orm import Session
from models.good.goods import AttributeSet, Attribute, ProductAttributeValue
from schemas.good.attrs import AttributeSetCreate, AttributeCreate, ProductAttributeValueCreate
from sqlalchemy.orm import joinedload
# AttributeSet CRUD
def create_attribute_set(db: Session, attribute_set: AttributeSetCreate):
    """Create a new attribute set in the database.
    
    Args:
        db (Session): SQLAlchemy database session
        attribute_set (AttributeSetCreate): Pydantic model containing attribute set data
        
    Returns:
        AttributeSet: The newly created attribute set
    """
    db_attribute_set = AttributeSet(**attribute_set.dict())
    db.add(db_attribute_set)
    db.commit()
    db.refresh(db_attribute_set)
    return db_attribute_set

def get_attribute_set(db: Session, attribute_set_id: int):
    """Get an attribute set by ID with its associated attributes.
    
    Args:
        db (Session): SQLAlchemy database session
        attribute_set_id (int): ID of the attribute set to retrieve
        
    Returns:
        AttributeSet: The requested attribute set with attributes loaded
    """
    attribute_set = db.query(AttributeSet).options(joinedload(AttributeSet.attributes)).filter(AttributeSet.id == attribute_set_id).first()
    return attribute_set
# Attribute CRUD
def create_attribute(db: Session, attribute: AttributeCreate):
    """Create a new attribute in the database.
    
    Args:
        db (Session): SQLAlchemy database session
        attribute (AttributeCreate): Pydantic model containing attribute data
        
    Returns:
        Attribute: The newly created attribute
    """
    db_attribute = Attribute(**attribute.dict())
    db.add(db_attribute)
    db.commit()
    db.refresh(db_attribute)
    return db_attribute

def get_attribute(db: Session, attribute_id: int):
    """Get an attribute by ID.
    
    Args:
        db (Session): SQLAlchemy database session
        attribute_id (int): ID of the attribute to retrieve
        
    Returns:
        Attribute: The requested attribute or None if not found
    """
    return db.query(Attribute).filter(Attribute.id == attribute_id).first()

# ProductAttributeValue CRUD
def create_product_attribute_value(db: Session, product_attribute_value: ProductAttributeValueCreate):
    """Create a new product-attribute value association in the database.
    
    Args:
        db (Session): SQLAlchemy database session
        product_attribute_value (ProductAttributeValueCreate): Pydantic model containing association data
        
    Returns:
        ProductAttributeValue: The newly created association
    """
    db_value = ProductAttributeValue(**product_attribute_value.dict())
    db.add(db_value)
    db.commit()
    db.refresh(db_value)
    return db_value

def get_product_attribute_value(db: Session, good_id: int, attribute_id: int):
    """Get a product-attribute value association by product and attribute IDs.
    
    Args:
        db (Session): SQLAlchemy database session
        good_id (int): ID of the product
        attribute_id (int): ID of the attribute
        
    Returns:
        ProductAttributeValue: The requested association or None if not found
    """
    return db.query(ProductAttributeValue).filter(
        ProductAttributeValue.good_id == good_id,
        ProductAttributeValue.attribute_id == attribute_id
    ).first()

def get_all_product_attribute_values(db: Session, good_id: int):
    """Get all attribute values associated with a product.
    
    Args:
        db (Session): SQLAlchemy database session
        good_id (int): ID of the product
        
    Returns:
        List[ProductAttributeValue]: All attribute values for the specified product
    """
    return db.query(ProductAttributeValue).filter(ProductAttributeValue.good_id == good_id).all()
