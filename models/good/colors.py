from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database import Base
from .associations import good_color_association

class Color(Base):
    """
    Represents a color entity in the database with many-to-many relationship to Goods.
    
    Attributes:
        id (int): Primary key identifier for the color.
        name (str): Unique name of the color (must be unique across all colors).
        code (str): Path or URL to the color representation (image/hex code/etc).
        goods (relationship): Many-to-many relationship with Goods through the 
            good_color_association table.
    
    Table configuration:
        __tablename__: 'color' - matches ForeignKey in association table
        __table_args__: {'extend_existing': True} ensures proper table creation order
    """
    __tablename__ = "color"  # Ensure table name matches ForeignKey in association table

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)  # Name of the color with unique constraint
    code = Column(String, nullable=False)  # Path or URL to the image

    # Relationship to Good (many-to-many)
    goods = relationship("models.good.goods.Good", secondary=good_color_association, back_populates="colors")

    __table_args__ = {'extend_existing': True}  # Ensures proper table creation order
