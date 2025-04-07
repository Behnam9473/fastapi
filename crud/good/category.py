"""
Category CRUD operations module.

This module provides CRUD (Create, Read, Update, Delete) operations for product categories,
including hierarchical category management and image handling.

Key Features:
- Category creation with optional parent-child relationships
- Full category hierarchy traversal
- Image handling for categories (URLs, file uploads, local paths)
- Comprehensive CRUD operations via CategoryCRUD class
"""
from pathlib import Path
from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from models.good.goods import Category
from schemas.good.category import CategoryCreate, CategoryUpdate, CategoryResponse
from fastapi import HTTPException
import requests

def save_image(image) -> Optional[str]:
    """
    Save category image from various sources and return the saved path.
    
    Handles three types of image inputs:
    1. URLs (http/https) - downloads the image
    2. Local file paths - copies the file
    3. Uploaded file objects - saves the file
    
    Args:
        image: Can be either:
            - str: URL or local file path
            - UploadFile: FastAPI uploaded file object
            - None: No image to save
    
    Returns:
        Optional[str]: Path to saved image relative to media/categories,
                      or None if no image was provided
    
    Raises:
        HTTPException: If there's an error saving the image (status_code=500)
    """
    if not image:
        return None
        
    # Create media/categories directory if it doesn't exist
    save_path = Path("./media/categories")
    save_path.mkdir(parents=True, exist_ok=True)
    
    try:
        if isinstance(image, str):
            # Check if it's a URL
            if image.startswith(('http://', 'https://')):
                response = requests.get(image)
                response.raise_for_status()
                
                # Generate filename from URL
                url_path = Path(image.split('?')[0])  # Remove query parameters
                safe_name = url_path.name[:50]   # Limit filename length
                file_path = save_path / safe_name
                
                # Save the downloaded image
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                return f"./media/categories/{safe_name}"
            else:
                # Handle local file path
                source_path = Path(image)
                safe_name = source_path.stem
                file_path = save_path / safe_name
                
                # Copy the image
                with open(source_path, "rb") as src, open(file_path, "wb") as dst:
                    dst.write(src.read())
                return f"./media/categories/{safe_name}"
        else:
            # Handle uploaded file objects
            filename = image.filename
            safe_name = Path(filename).stem + ".jpg"
            file_path = save_path / safe_name
            
            # Save the image
            with open(file_path, "wb") as f:
                f.write(image.file.read())
            return f"./media/categories/{safe_name}"
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving image: {str(e)}")



def delete_category(db: Session, category_id: int) -> Optional[CategoryResponse]:
    """
    Delete a category by ID and return its information before deletion.
    
    Args:
        db: SQLAlchemy database session
        category_id: ID of the category to delete
    
    Returns:
        Optional[CategoryResponse]: Deleted category information if found,
                                   None if category doesn't exist
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        return None
    
    # Store category info before deletion
    category_response = CategoryResponse(
        id=category.id,
        name=category.name,
        parent_id=category.parent_id,
        image=category.image,
        children=[]
    )
    
    db.delete(category)
    db.commit()
    return category_response

def update_category(db: Session, category_id: int, category_data: CategoryUpdate) -> Optional[CategoryResponse]:
    """
    Update category information.
    
    Args:
        db: SQLAlchemy database session
        category_id: ID of the category to update
        category_data: CategoryUpdate model with new values
    
    Returns:
        Optional[CategoryResponse]: Updated category information if found,
                                   None if category doesn't exist
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        return None
    
    for key, value in category_data.dict(exclude_unset=True).items():
        setattr(category, key, value)
    
    db.commit()
    db.refresh(category)
    return CategoryResponse(id=category.id, name=category.name, parent_id=category.parent_id, image=category.image, children=[])

def get_category_with_children(db: Session, category_id: int) -> Optional[CategoryResponse]:
    """
    Get a category with all its children recursively.
    
    Args:
        db: SQLAlchemy database session
        category_id: ID of the parent category
    
    Returns:
        Optional[CategoryResponse]: Category with nested children if found,
                                   None if category doesn't exist
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        return None
    
    children = db.query(Category).filter(Category.parent_id == category_id).all()
    category_dict = {
        "id": category.id,
        "name": category.name,
        "parent_id": category.parent_id,
        "image": category.image,
        "children": [get_category_with_children(db, child.id) for child in children]
    }
    return CategoryResponse(**category_dict)

class CategoryCRUD:
    """
    Comprehensive CRUD operations for product categories.
    
    Provides methods for:
    - Creating categories with hierarchical relationships
    - Retrieving categories in various formats (single, tree, hierarchy)
    - Updating category information
    - Deleting categories
    - Special queries like ancestors and leaf categories
    """
    def __init__(self, db: Session):
        """
        Initialize CategoryCRUD with a database session.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def create(self, category_data: CategoryCreate) -> CategoryResponse:
        """
        Create a new category with optional parent relationship.
        
        Args:
            category_data: CategoryCreate model with:
                - name: Category name
                - parent_id: Optional parent category ID
                - image: Optional image (URL, path, or upload)
        
        Returns:
            CategoryResponse: Created category with calculated levels
        
        Raises:
            HTTPException: If creation fails (status_code=500)
                          or category not found after creation (status_code=404)
        """
        try:
            # Save image and get path if image exists
            image_path = None
            if category_data.image:
                image_path = save_image(category_data.image)
            
            # Create category with image path
            db_category = Category(
                name=category_data.name,
                parent_id=category_data.parent_id,
                image=image_path
            )
            self.db.add(db_category)
            self.db.commit()
            self.db.refresh(db_category)
            
            # Reload the category with its children
            loaded_category = (
                self.db.query(Category)
                .options(joinedload(Category.children))
                .filter(Category.id == db_category.id)
                .first()
            )
            
            if loaded_category is None:
                raise HTTPException(status_code=404, detail="Category not found after creation")

            # Convert to response model
            category_response = CategoryResponse(
                id=loaded_category.id,
                name=loaded_category.name,
                parent_id=loaded_category.parent_id,
                image=loaded_category.image,
                children=[]
            )
            category_response.calculate_levels()
            return category_response

        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    def get_by_id(self, category_id: int) -> CategoryResponse:
        """
        Get a single category by ID with immediate children.
        
        Args:
            category_id: ID of the category to retrieve
        
        Returns:
            CategoryResponse: Category with immediate children
        
        Raises:
            HTTPException: If category not found (status_code=404)
        """
        db_category = (
            self.db.query(Category)
            .filter(Category.id == category_id)
            .first()
        )
        
        if db_category is None:
            raise HTTPException(status_code=404, detail="Category not found")

        children = (
            self.db.query(Category)
            .filter(Category.parent_id == category_id)
            .all()
        )

        category_dict = {
            "id": db_category.id,
            "name": db_category.name,
            "parent_id": db_category.parent_id,
            "image": db_category.image,
            "children": [
                {
                    "id": child.id,
                    "name": child.name,
                    "parent_id": child.parent_id,
                    "image": child.image,
                    "children": []
                }
                for child in children
            ]
        }
        
        category_response = CategoryResponse(**category_dict)
        category_response.calculate_levels()
        return category_response

    def get_ancestors(self, category_id: int) -> List[CategoryResponse]:
        """
        Get all ancestor categories (parent chain) for a category.
        
        Args:
            category_id: ID of the category to find ancestors for
        
        Returns:
            List[CategoryResponse]: List of ancestor categories from direct parent to root
        """
        ancestors = []
        current_category = (
            self.db.query(Category)
            .filter(Category.id == category_id)
            .first()
        )
        
        while current_category and current_category.parent_id:
            parent = (
                self.db.query(Category)
                .filter(Category.id == current_category.parent_id)
                .first()
            )
            if parent:
                ancestors.append(CategoryResponse(
                    id=parent.id,
                    name=parent.name,
                    parent_id=parent.parent_id,
                    image=parent.image,
                    children=[]
                ))
                current_category = parent
            else:
                break
                
        return ancestors

    def get_hierarchy(self, category_id: int) -> CategoryResponse:
        """
        Get full category hierarchy starting from specified category.
        
        Args:
            category_id: ID of the root category for the hierarchy
        
        Returns:
            CategoryResponse: Complete category tree starting from specified ID
        
        Raises:
            HTTPException: If category not found (status_code=404)
        """
        category = get_category_with_children(self.db, category_id)
        if category is None:
            raise HTTPException(status_code=404, detail="Category not found")
        return category

    def get_all(self) -> List[CategoryResponse]:
        """
        Get all root categories with their complete hierarchies.
        
        Returns:
            List[CategoryResponse]: List of all root categories with nested children
        """
        root_categories = self.db.query(Category).filter(Category.parent_id == None).all()
        return [get_category_with_children(self.db, category.id) for category in root_categories]
    


    def get_tree(self) -> List[CategoryResponse]:
        """
        Alias for get_all() - returns all root categories with hierarchies.
        
        Returns:
            List[CategoryResponse]: List of all root categories with nested children
        """
        root_categories = self.db.query(Category).filter(Category.parent_id == None).all()
        return [get_category_with_children(self.db, category.id) for category in root_categories]

    def get_leafs_categories(self) -> List[CategoryResponse]:
        """
        Get all leaf categories (categories without children).
        
        Returns:
            List[CategoryResponse]: List of leaf categories
        """
        leaf_categories = self.db.query(Category).filter(Category.children == []).all()
        return [CategoryResponse(
            id=cat.id,
            name=cat.name,
            parent_id=cat.parent_id,
            image=cat.image,
            children=[]
        ) for cat in leaf_categories]

    def update(self, category_id: int, category_data: CategoryUpdate) -> CategoryResponse:
        """
        Update category information.
        
        Args:
            category_id: ID of the category to update
            category_data: CategoryUpdate model with new values
        
        Returns:
            CategoryResponse: Updated category information
        
        Raises:
            HTTPException: If category not found (status_code=404)
        """
        updated_category = update_category(self.db, category_id, category_data)
        if updated_category is None:
            raise HTTPException(status_code=404, detail="Category not found")
        return updated_category

    def delete(self, category_id: int) -> CategoryResponse:
        """
        Delete a category by ID.
        
        Args:
            category_id: ID of the category to delete
        
        Returns:
            CategoryResponse: Information about the deleted category
        
        Raises:
            HTTPException: If category not found (status_code=404)
        """
        deleted_category = delete_category(self.db, category_id)
        if deleted_category is None:
            raise HTTPException(status_code=404, detail="Category not found")
        return deleted_category