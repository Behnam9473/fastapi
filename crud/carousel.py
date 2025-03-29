# 1. Utility Functions
from pathlib import Path
import shutil
from typing import List, Optional

from fastapi import HTTPException, requests
from crud.base import CRUDBase
from models.carousel import CarouselImage
from schemas.carousel import CarouselImageCreate, CarouselImageUpdate
from sqlalchemy.orm import Session

# async def save_image(image) -> Optional[str]:
#     """Save category image from URL or local upload and return the saved path"""
#     if not image:
#         return None
        
#     # Create media/carousel directory if it doesn't exist
#     save_path = Path("./media/carousel")
#     save_path.mkdir(parents=True, exist_ok=True)
    
#     try:
#         if isinstance(image, str):
#             # Check if it's a URL
#             if image.startswith(('http://', 'https://')):
#                 response = requests.get(image)
#                 response.raise_for_status()
                
#                 # Generate filename from URL
#                 url_path = Path(image.split('?')[0])  # Remove query parameters
#                 safe_name = url_path.name[:50] + ".jpg"  # Limit filename length
#                 file_path = save_path / safe_name
                
#                 # Save the downloaded image
#                 with open(file_path, 'wb') as f:
#                     f.write(response.content)
#                 return f"./media/carousel/{safe_name}"
#             else:
#                 # Handle local file path
#                 source_path = Path(image)
#                 safe_name = source_path.stem + ".jpg"
#                 file_path = save_path / safe_name
                
#                 # Copy the image
#                 with open(source_path, "rb") as src, open(file_path, "wb") as dst:
#                     dst.write(src.read())
#                 return f"./media/carousel/{safe_name}"
#         else:
#             # Handle uploaded file objects
#             filename = image.filename
#             safe_name = Path(filename).stem + ".jpg"
#             file_path = save_path / safe_name
            
#             # Save the image
#             with open(file_path, "wb") as f:
#                 f.write(image.file.read())
#             return f"./media/carousel/{safe_name}"
            
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error saving image: {str(e)}")

# 2. CRUD Class
class CRUDCarousel(CRUDBase[CarouselImage, CarouselImageCreate, CarouselImageUpdate]):
    # Basic CRUD operations
    def get(self, db: Session, id: int) -> Optional[CarouselImage]:
        return db.query(self.model).filter(self.model.id == id).first()
    
    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 10) -> List[CarouselImage]:
        return db.query(self.model).offset(skip).limit(limit).all()
    
    def create(self, db: Session, image_data: CarouselImageCreate):
        db_image = CarouselImage(
            image=image_data.image,
            image_alternate_text=image_data.image_alternate_text,
            description=image_data.description,
            price=image_data.price,
            url=image_data.url,
            btn_x_coordinate=image_data.btn_x_coordinate,
            btn_y_coordinate=image_data.btn_y_coordinate,
        )
        db.add(db_image)
        db.commit()
        db.refresh(db_image)
        return db_image
    
    def update(self, db: Session, *, id: int, obj_in: CarouselImageUpdate) -> Optional[CarouselImage]:
        db_obj = self.get(db, id=id)
        if db_obj:
            update_data = obj_in.model_dump()
            for field, value in update_data.items():
                setattr(db_obj, field, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, *, id: int) -> Optional[CarouselImage]:
        db_obj = self.get(db, id=id)
        if db_obj:
            self._delete_image_file(db_obj.image)
            db.delete(db_obj)
            db.commit()
        return db_obj

    # Custom query methods
    def get_by_image_path(self, db: Session, *, image_path: str) -> Optional[CarouselImage]:
        return db.query(CarouselImage).filter(CarouselImage.image == image_path).first()
    


    # Helper methods
    def _delete_image_file(self, image_path: str) -> None:
        path = Path(image_path)
        if path.exists():
            path.unlink()

# 3. Instance Creation
carousel = CRUDCarousel(CarouselImage)
