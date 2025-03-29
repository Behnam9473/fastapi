# Standard library imports
from typing import List

# Third-party imports
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

# Local application imports
from database import get_db
from schemas.good.attrs import (
    Attribute,
    AttributeCreate,
    AttributeSet,
    AttributeSetCreate,
    ProductAttributeValue,
    ProductAttributeValueCreate
)
import crud.good.attr as crud

router = APIRouter(prefix= "", tags=["attributes"])

# AttributeSet Endpoints
@router.post("/attribute-sets/", response_model=AttributeSet)
def create_attribute_set(attribute_set: AttributeSetCreate, db: Session = Depends(get_db)):
    """ Description: This creates a new group of attributes (called an AttributeSet) that belongs to a specific category.
            {
            "name": "Technical Specifications",
            "category_id": 1
            }
                
    """
    return crud.create_attribute_set(db=db, attribute_set=attribute_set)

@router.get("/attribute-sets/{attribute_set_id}", response_model=AttributeSet)
def get_attribute_set(attribute_set_id: int, db: Session = Depends(get_db)):
    """Description: Retrieve a specific AttributeSet by its ID, including its attributes.

        Path Parameter:

        attribute_set_id - The unique ID of the AttributeSet.

        Response Example:

        json
        {
        "id": 1,
        "name": "Technical Specifications",
        "category_id": 1,
        "attributes": [
            {
            "id": 1,
            "name": "Weight",
            "data_type": "float",
            "unit": "kg"
            }
        ]
        }
"""
    db_attribute_set = crud.get_attribute_set(db, attribute_set_id)
    print(db_attribute_set)
    if not db_attribute_set:
        raise HTTPException(status_code=404, detail="AttributeSet not found")
    return db_attribute_set


# Attribute Endpoints
@router.post("/attributes/", response_model=Attribute)
def create_attribute(attribute: AttributeCreate, db: Session = Depends(get_db)):
    """ 
    Description: Add a new attribute (e.g., "Color" or "Weight") to an AttributeSet.

    Request Body Example:
    {
    "name": "Weight",
    "attribute_set_id": 1,
    "data_type": "float",
    "unit": "kg"
    }
    """
    return crud.create_attribute(db=db, attribute=attribute)

@router.get("/attributes/{attribute_id}", response_model=Attribute)
def get_attribute(attribute_id: int, db: Session = Depends(get_db)):
    """
    Description: Retrieve an attribute by its ID.

    Path Parameter:

    attribute_id - The unique ID of the Attribute.
    
    """
    db_attribute = crud.get_attribute(db, attribute_id)
    if not db_attribute:
        raise HTTPException(status_code=404, detail="Attribute not found")
    return db_attribute

# ProductAttributeValue Endpoints
@router.post("/product-attribute-values/", response_model=ProductAttributeValue)
def create_product_attribute_value(product_attribute_value: ProductAttributeValueCreate, db: Session = Depends(get_db)):
    """
    Description: Save a specific value for an attribute (e.g., "Weight = 2.5 kg") for a specific product (Good).

    Request Body Example:

    {
    "good_id": 10,
    "attribute_id": 1,
    "value_float": 2.5
    }
    
    """
    return crud.create_product_attribute_value(db=db, product_attribute_value=product_attribute_value)

@router.get("/product-attribute-values/{good_id}/{attribute_id}", response_model=ProductAttributeValue)
def get_product_attribute_value(good_id: int, attribute_id: int, db: Session = Depends(get_db)):
    """ 
    Description: Retrieve the value of a specific attribute for a given product (Good).
    Path Parameters:

    good_id - The unique ID of the product.

    attribute_id - The unique ID of the attribute.
    """
    db_value = crud.get_product_attribute_value(db, good_id, attribute_id)
    if not db_value:
        raise HTTPException(status_code=404, detail="ProductAttributeValue not found")
    return db_value

@router.get("/product-attribute-values/{good_id}", response_model=List[ProductAttributeValue])
def get_all_product_attributes(good_id: int, db: Session = Depends(get_db)):
    """
    Description: Retrieve all attributes and their values for a given product (Good).
    Path Parameters:
        good_id - The unique ID of the product.
    """
    db_values = crud.get_all_product_attribute_values(db, good_id)
    if not db_values:
        raise HTTPException(status_code=404, detail="No attributes found for the specified good_id")
    return db_values
