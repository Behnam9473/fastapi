from sqlalchemy import Column, Integer, String, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from database import Base


class CarouselImage(Base):
    """
    Represents a carousel image in the database with associated metadata.
    
    Attributes:
        id (int): Primary key identifier for the carousel image.
        image (str): Path or URL to the image file. Required.
        image_alternate_text (str): Alternate text for accessibility. Required.
        description (JSON): Detailed description of the image content in JSON format. Required.
        price (JSON): Pricing information in JSON format. Required.
        url (JSON): Associated URL(s) in JSON format. Required.
        btn_x_coordinate (JSON): X coordinate for button placement in JSON format. Required.
        btn_y_coordinate (JSON): Y coordinate for button placement in JSON format. Required.
    """
    __tablename__ = "carousel"

    id = Column(Integer, primary_key=True, index=True)
    image = Column(String, nullable=False)  # Path or URL to the image
    image_alternate_text = Column(String, nullable=False)  # Alternate text for the image

    description = Column(JSON, nullable=False)  # Description text
    price = Column(JSON, nullable=False)  # Description text
    url = Column(JSON, nullable=False)  # Description text

    btn_x_coordinate = Column(JSON, nullable=False)  # X coordinate for the button
    btn_y_coordinate = Column(JSON, nullable=False)  # Y coordinate for the button

