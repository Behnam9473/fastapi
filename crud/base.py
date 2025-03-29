from typing import Generic, TypeVar, Type, Optional, List, Dict, Any, Protocol
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.ext.declarative import DeclarativeMeta
from abc import ABC, abstractmethod

ModelType = TypeVar("ModelType", bound=DeclarativeMeta)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class Readable(Protocol, Generic[ModelType]):
    def get(self, db: Session, id: Any) -> Optional[ModelType]: ...
    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[ModelType]: ...

class Creatable(Protocol, Generic[ModelType, CreateSchemaType]):
    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType: ...

class Updatable(Protocol, Generic[ModelType, UpdateSchemaType]):
    def update(self, db: Session, *, db_obj: ModelType, obj_in: UpdateSchemaType) -> ModelType: ...

class Deletable(Protocol, Generic[ModelType]):
    def remove(self, db: Session, *, id: int) -> ModelType: ...

class CRUDBase(ABC, Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Base class for CRUD operations.
    Implements all CRUD protocols but allows subclasses to implement only what they need.
    """
    def __init__(self, model: type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).
        
        **Parameters**
        * `model`: A SQLAlchemy model class
        """
        self.model = model

    @abstractmethod
    def get(self, db: Session, id: int) -> Optional[ModelType]:
        pass

    @abstractmethod
    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 10) -> List[ModelType]:
        pass

    @abstractmethod
    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        pass

    @abstractmethod
    def update(self, db: Session, *, id: int, obj_in: UpdateSchemaType) -> Optional[ModelType]:
        pass

    @abstractmethod
    def delete(self, db: Session, *, id: int) -> Optional[ModelType]:
        pass

class ReadOnlyCRUD(CRUDBase[ModelType, CreateSchemaType, UpdateSchemaType], Readable[ModelType]):
    """A CRUD class that only implements read operations"""
    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        raise NotImplementedError("This is a read-only CRUD")

    def update(self, db: Session, *, db_obj: ModelType, obj_in: UpdateSchemaType) -> ModelType:
        raise NotImplementedError("This is a read-only CRUD")

    def remove(self, db: Session, *, id: int) -> ModelType:
        raise NotImplementedError("This is a read-only CRUD") 