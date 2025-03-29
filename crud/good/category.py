from pathlib import Path
from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from models.good.goods import Category
from schemas.good.category import CategoryCreate, CategoryUpdate, CategoryResponse
from fastapi import HTTPException
import requests

def save_image(image) -> Optional[str]:
    """Save category image from URL or local upload and return the saved path"""
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
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        return None
    
    for key, value in category_data.dict(exclude_unset=True).items():
        setattr(category, key, value)
    
    db.commit()
    db.refresh(category)
    return CategoryResponse(id=category.id, name=category.name, parent_id=category.parent_id, image=category.image, children=[])

def get_category_with_children(db: Session, category_id: int) -> Optional[CategoryResponse]:
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
    def __init__(self, db: Session):
        self.db = db

    def create(self, category_data: CategoryCreate) -> CategoryResponse:
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
        category = get_category_with_children(self.db, category_id)
        if category is None:
            raise HTTPException(status_code=404, detail="Category not found")
        return category

    def get_all(self) -> List[CategoryResponse]:
        root_categories = self.db.query(Category).filter(Category.parent_id == None).all()
        return [get_category_with_children(self.db, category.id) for category in root_categories]
    


    def get_tree(self) -> List[CategoryResponse]:
        root_categories = self.db.query(Category).filter(Category.parent_id == None).all()
        return [get_category_with_children(self.db, category.id) for category in root_categories]

    def get_leafs_categories(self) -> List[CategoryResponse]:
        leaf_categories = self.db.query(Category).filter(Category.children == []).all()
        return [CategoryResponse(
            id=cat.id,
            name=cat.name,
            parent_id=cat.parent_id,
            image=cat.image,
            children=[]
        ) for cat in leaf_categories]

    def update(self, category_id: int, category_data: CategoryUpdate) -> CategoryResponse:
        updated_category = update_category(self.db, category_id, category_data)
        if updated_category is None:
            raise HTTPException(status_code=404, detail="Category not found")
        return updated_category

    def delete(self, category_id: int) -> CategoryResponse:
        deleted_category = delete_category(self.db, category_id)
        if deleted_category is None:
            raise HTTPException(status_code=404, detail="Category not found")
        return deleted_category