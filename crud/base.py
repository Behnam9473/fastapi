from typing import Generic, TypeVar, Type, Optional, List, Dict, Any, Protocol
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.ext.declarative import DeclarativeMeta
from abc import ABC, abstractmethod

ModelType = TypeVar("ModelType", bound=DeclarativeMeta)
udCreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaserModel)

class Readable(Protocol, Generic[ModelType]):
    """Protocol defining read operations for a model.
    
    Classes implementing this protocol must provide methods to:
    - Get a single item by ID
    - Get multiple items with pagination
    """
    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """Get a single item by its ID.
        
        Args:
            db: SQLAlchemy Session
            id: ID of item to retrieve
            
        Returns:
            The model instance if found, else None
        """
        ...
    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Get multiple items with pagination.
        
        Args:
            db: SQLAlchemy Session
            skip: Number of items to skip (for pagination)
            limit: Maximum number of items to return
            
        Returns:
            List of model instances
        """
        ...

class Creatable(Protocol, Generic[ModelType, CreateSchemaType]):
    """Protocol defining create operation for a model.
    
    Classes implementing this protocol must provide method to create new items.
    """
    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """Raises NotImplementedError as this is a read-only CRUD."""
        """Create a new item.
        
        Args:
            db: SQLAlchemy Session
            obj_in: Pydantic schema with data for new item
            
        Returns:
            The newly created model instance
        """
        ...

class Updatable(Protocol, Generic[ModelType, UpdateSchemaType]):
    """Protocol defining update operation for a model.
    
    Classes implementing this protocol must provide method to update existing items.
    """
    def update(self, db: Session, *, db_obj: ModelType, obj_in: UpdateSchemaType) -> ModelType:
        """Raises NotImplementedError as this is a read-only CRUD."""
        """Update an existing item.
        
        Args:
            db: SQLAlchemy Session
            db_obj: Existing model instance to update
            obj_in: Pydantic schema with update data
            
        Returns:
            The updated model instance
        """
        ...

class Deletable(Protocol, Generic[ModelType]):
    """Protocol defining delete operation for a model.
    
    Classes implementing this protocol must provide method to delete items.
    """
    def remove(self, db: Session, *, id: int) -> ModelType:
        """Raises NotImplementedError as this is a read-only CRUD."""
        """Delete an item by its ID.
        
        Args:
            db: SQLAlchemy Session
            id: ID of item to delete
            
        Returns:
            The deleted model instance
        """
        ...

class CRUDBase(ABC, Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Abstract base class for CRUD operations.
    
    Implements all CRUD protocols but requires subclasses to implement all methods.
    Provides a standard interface for Create, Read, Update, Delete operations.
    """
    """
    Base class for CRUD operations.
    Implements all CRUD protocols but allows subclasses to implement only what they need.
    """
    def __init__(self, model: type[ModelType]):
        """Initialize CRUD operations for a specific model.
        
        Args:
            model: SQLAlchemy model class to perform operations on
        """
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).
        
        **Parameters**
        * `model`: A SQLAlchemy model class
        """
        self.model = model

    @abstractmethod
    def get(self, db: Session, id: int) -> Optional[ModelType]:
        """Get a single item by ID.
        
        Args:
            db: SQLAlchemy Session
            id: ID of item to retrieve
            
        Returns:
            The model instance if found, else None
        """
        pass

    @abstractmethod
    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 10) -> List[ModelType]:
        """Get multiple items with pagination.
        
        Args:
            db: SQLAlchemy Session
            skip: Number of items to skip (for pagination)
            limit: Maximum number of items to return
            
        Returns:
            List of model instances
        """
        pass

    @abstractmethod
    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """Raises NotImplementedError as this is a read-only CRUD."""
        """Create a new item.
        
        Args:
            db: SQLAlchemy Session
            obj_in: Pydantic schema with data for new item
            
        Returns:
            The newly created model instance
        """
        pass

    @abstractmethod
    def update(self, db: Session, *, id: int, obj_in: UpdateSchemaType) -> Optional[ModelType]:
        """Update an existing item.
        
        Args:
            db: SQLAlchemy Session
            id: ID of item to update
            obj_in: Pydantic schema with update data
            
        Returns:
            The updated model instance if found, else None
        """
        pass

    @abstractmethod
    def delete(self, db: Session, *, id: int) -> Optional[ModelType]:
        """Delete an item by its ID.
        
        Args:
            db: SQLAlchemy Session
            id: ID of item to delete
            
        Returns:
            The deleted model instance if found, else None
        """
        pass

class ReadOnlyCRUD(CRUDBase[ModelType, CreateSchemaType, UpdateSchemaType], Readable[ModelType]):
    """CRUD class that only implements read operations.
    
    Raises NotImplementedError for any write operations (create/update/delete).
    """
    """A CRUD class that only implements read operations"""
    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """Raises NotImplementedError as this is a read-only CRUD."""
        raise NotImplementedError("This is a read-only CRUD")

    def update(self, db: Session, *, db_obj: ModelType, obj_in: UpdateSchemaType) -> ModelType:
        """Raises NotImplementedError as this is a read-only CRUD."""
        raise NotImplementedError("This is a read-only CRUD")

    def remove(self, db: Session, *, id: int) -> ModelType:
        """Raises NotImplementedError as this is a read-only CRUD."""
        raise NotImplementedError("This is a read-only CRUD")