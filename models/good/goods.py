from sqlalchemy import Boolean, Column, Integer, String, Float, ForeignKey, JSON, DateTime, Table, UUID
from sqlalchemy.orm import relationship, validates, object_session
from database import Base
import pytz
from datetime import datetime
from .associations import good_color_association
from .colors import Color
import hashlib
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import Enum


data_type_enum = Enum("string", "integer", "float", "boolean", "list", "json", name="data_type_enum")

# Utility function to generate SKU for goods
def generate_sku(good):
    """
    Generates a unique SKU (Stock Keeping Unit) for a good.
    
    Args:
        good (Good): The product object to generate SKU for
        
    Returns:
        str: Generated SKU in format ZAR-{5_digit_hash}{3_digit_id}
        
    Example:
        >>> generate_sku(good)
        'ZAR-12345678'
    """
    # Prefix for all SKUs
    prefix = "ZAR"

    # Generate a unique numeric code based on the product's name and ID
    unique_code_source = f"{good.name}{good.id}"
    unique_code_hash = hashlib.md5(unique_code_source.encode()).hexdigest()

    # Extract digits from the hash and zero-pad if necessary to make it 5 digits
    numeric_code = "".join(filter(str.isdigit, unique_code_hash))[:5].zfill(5)

    # Use the full good ID, zero-padded to ensure it's 3 digits minimum
    id_code = str(good.id).zfill(3)

    # Combine prefix, numeric code, and good ID to form the SKU with a hyphen
    sku = f"{prefix}-{numeric_code}{id_code}"

    return sku


class Category(Base):
    """
    Category model for organizing goods with subcategories.
    
    Attributes:
        id (int): Primary key
        name (str): Unique category name
        parent_id (int): Foreign key to parent category (nullable)
        image (str): Path to category image
        
    Relationships:
        goods: Related products in this category
        children: Subcategories of this category
        attribute_sets: Attribute sets associated with this category
    """
    __tablename__ = "category"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    parent_id = Column(Integer, ForeignKey("category.id"), nullable=True)  # Add parent_id
    image = Column(String, nullable=False) # Add image column

    # Relationships
    goods = relationship("Good", back_populates="category", cascade="all, delete-orphan")
    # Define the relationship
    children = relationship("Category",
                            backref="parent",
                            cascade="all, delete-orphan",
                            remote_side=[id],
                            single_parent=True)
    attribute_sets = relationship("AttributeSet", back_populates="category", cascade="all, delete-orphan")

    @property
    def is_leaf(self):
        """
        Check if the category is a leaf node (has no children).
        
        Returns:
            bool: True if category has no children, False otherwise
            
        Raises:
            ValueError: If category is not bound to a session
        """
        session = object_session(self)
        if session is None:
            raise ValueError("Category is not bound to a session.")

        # Explicitly query for children
        has_children = session.query(Category).filter(Category.parent_id == self.id).first() is not None
        print(f"Category ID: {self.id}, Has Children: {has_children}")  # Debug log
        return not has_children

    @property
    def get_hierarchy(self):
        """
        Get the full hierarchical path of the category.
        
        Returns:
            str: Full path from root to current category
            
        Example:
            'Parent > Child > Current'
        """
        if self.parent:
            return f"{self.parent.get_hierarchy} > {self.name}"
        return self.name

    @classmethod
    def get_leaf_categories(cls, db):
        """
        Get all leaf categories (categories with no children).
        
        Args:
            db (Session): Database session
            
        Returns:
            List[Category]: List of leaf categories
        """
        return db.query(cls).filter(~cls.id.in_(
            db.query(cls.parent_id).filter(cls.parent_id.isnot(None))
        )).all()
    def get_ancestors(self, db: Session):
        """
        Get all ancestor categories of this category.
        
        Args:
            db (Session): Database session
            
        Returns:
            List[Category]: List of ancestor categories ordered from parent to root
        """
        ancestors = []
        current = self
        while current.parent_id is not None:
            current = db.query(Category).filter(Category.id == current.parent_id).first()
            if current:
                ancestors.append(current)
        return ancestors
class Good(Base):
    """
    Good (Product) model with detailed product information.
    
    Attributes:
        id (int): Primary key
        name (str): Product name
        description (str): Product description
        weight (float): Product weight
        dimensions (length, height, width): Product dimensions
        sku (str): Unique stock keeping unit
        tenant_id (UUID): Tenant identifier
        is_validated (bool): Validation status
        superuser_description (str): Admin notes
        status (str): Product status (pending/approved/declined)
        images (JSON): List of product image paths
        created_at (DateTime): Creation timestamp
        updated_at (DateTime): Last update timestamp
        
    Relationships:
        category: Product category
        colors: Available colors
        inventories: Stock information
        attribute_values: Product specifications
    """
    __tablename__ = "good"
    __table_args__ = {'extend_existing': True}

    # Primary Fields
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)

    # Physical Attributes
    weight = Column(Float)
    length = Column(Integer)
    height = Column(Integer)
    width = Column(Integer)

    # Product Identification
    sku = Column(String, unique=True, index=True, nullable=True)
    tenant_id = Column(UUID, nullable=False)

    # Validation and Status Fields
    is_validated = Column(Boolean, default=False)
    superuser_description = Column(String)
    status = Column(String, default="pending")

    # Relationships
    category_id = Column(Integer, ForeignKey("category.id", ondelete="CASCADE"), nullable=False)
    category = relationship("Category", back_populates="goods")
    colors = relationship("models.good.colors.Color", secondary=good_color_association, back_populates="goods")
    inventories = relationship("models.inventory.inventory.Inventory", back_populates="good", cascade="all, delete-orphan")
    attribute_values = relationship("ProductAttributeValue", back_populates="good", cascade="all, delete-orphan")

    # Media Storage
    images = Column(JSON, nullable=False, default=list)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(pytz.UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(pytz.UTC), onupdate=lambda: datetime.now(pytz.UTC))

    @property
    def generate_and_set_sku(self):
        """
        Generates and sets SKU if product is approved and SKU doesn't exist.
        
        Returns:
            str: Generated SKU or existing SKU
            
        Note:
            Only generates SKU when status is 'approved' and sku is None
        """
        if self.status == "approved" and not self.sku:
            self.sku = generate_sku(self)
        return self.sku

    def update_status(self):
        """
        Updates product status based on validation and admin notes.
        
        Status transitions:
        - is_validated=True → 'approved'
        - !is_validated and superuser_description → 'declined'
        - Otherwise → 'pending'
        """
        if self.is_validated:
            self.status = "approved"
        elif not self.is_validated and self.superuser_description:
            self.status = "declined"
        else:
            self.status = "pending"

# New Models for Product Specifications
class AttributeSet(Base):
    """
    Group of product specifications associated with a category.
    
    Attributes:
        id (int): Primary key
        name (str): Attribute set name
        category_id (int): Related category ID
        
    Relationships:
        category: Parent category
        attributes: Individual attributes in this set
    """
    __tablename__ = "attribute_set"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category_id = Column(Integer, ForeignKey("category.id", ondelete="CASCADE"), nullable=False)

    # Relationships
    category = relationship("Category", back_populates="attribute_sets")
    attributes = relationship("Attribute", back_populates="attribute_set", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<AttributeSet(name='{self.name}')>"

class Attribute(Base):
    """
    Individual product specification within an attribute set.
    
    Attributes:
        id (int): Primary key
        name (str): Attribute name
        attribute_set_id (int): Parent attribute set ID
        data_type (Enum): Data type (string/integer/float/boolean/list/json)
        unit (str): Measurement unit if applicable
        
    Relationships:
        attribute_set: Parent attribute set
        values: Product attribute values
    """
    __tablename__ = "attribute"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    attribute_set_id = Column(Integer, ForeignKey("attribute_set.id", ondelete="CASCADE"), nullable=False)
    data_type = Column(data_type_enum, nullable=False)
    unit = Column(String, nullable=True)

    # Relationships
    attribute_set = relationship("AttributeSet", back_populates="attributes")
    values = relationship("ProductAttributeValue", back_populates="attribute", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Attribute(name='{self.name}', data_type='{self.data_type}')>"

class ProductAttributeValue(Base):
    """
    Value of a specific attribute for a product.
    
    Attributes:
        good_id (int): Related product ID (composite primary key)
        attribute_id (int): Related attribute ID (composite primary key)
        value_*: Value fields for different data types
        
    Relationships:
        good: Related product
        attribute: Related attribute
    """
    __tablename__ = "product_attribute_value"
    __table_args__ = {'extend_existing': True}

    good_id = Column(Integer, ForeignKey("good.id", ondelete="CASCADE"), primary_key=True)
    attribute_id = Column(Integer, ForeignKey("attribute.id", ondelete="CASCADE"), primary_key=True)
    value_string = Column(String, nullable=True)
    value_integer = Column(Integer, nullable=True)
    value_float = Column(Float, nullable=True)
    value_boolean = Column(Boolean, nullable=True)
    value_json = Column(JSON, nullable=True)

    # Relationships
    good = relationship("Good", back_populates="attribute_values")
    attribute = relationship("Attribute", back_populates="values")

    def __repr__(self):
        return f"<ProductAttributeValue(good_id={self.good_id}, attribute_id={self.attribute_id})>"