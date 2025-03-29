from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database import Base
from .associations import good_color_association

class Color(Base):
    __tablename__ = "color"  # Ensure table name matches ForeignKey in association table

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)  # Name of the color with unique constraint
    code = Column(String, nullable=False)  # Path or URL to the image

    # Relationship to Good (many-to-many)
    goods = relationship("models.good.goods.Good", secondary=good_color_association, back_populates="colors")

    __table_args__ = {'extend_existing': True}  # Ensures proper table creation order
