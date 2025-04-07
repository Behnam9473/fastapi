from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from database import Base
from utils.exceptions import AddressError
import re


class Address(Base):
    """
    Represents a customer's address in the database.
    
    Attributes:
        id (int): Primary key for the address.
        customer_id (int): Foreign key referencing the customer this address belongs to.
        province (str): The province of the address (required).
        city (str): The city of the address (required).
        street (str): The street of the address (required).
        alley (str): The alley of the address (optional).
        building (str): The building of the address (optional).
        number (int): The building number (required).
        postal_code (str): The 10-digit postal code (required).
        phone_number (str): Contact phone number (optional).
        latitude (float): Geographical latitude (optional).
        longitude (float): Geographical longitude (optional).
    """
    __tablename__ = 'addresses'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey('customer.id', ondelete="CASCADE"), nullable=False)
    province = Column(String(100), nullable=False)  # استان
    city = Column(String(100), nullable=False)      # شهر
    street = Column(String(200), nullable=False)    # خیابان
    alley = Column(String(200), nullable=True)      # کوچه
    building = Column(String(100), nullable=True)   # ساختمان
    number = Column(Integer, nullable=False)        # پلاک
    postal_code = Column(String(10), nullable=False)  # کد پستی
    phone_number = Column(String(20), nullable=True)  # شماره تماس
    latitude = Column(Float, nullable=True)         # عرض جغرافیایی
    longitude = Column(Float, nullable=True)        # طول جغرافیایی

    # Relationship with Customer model
    customer = relationship("Customer", back_populates="addresses")

    def __repr__(self):
        return f"<Address {self.id} for customer {self.customer_id}>"

    @staticmethod
    def validate_postal_code(postal_code: str) -> None:
        """
        Validate that a postal code follows the correct format (10 digits).
        
        Args:
            postal_code (str): The postal code to validate.
            
        Raises:
            AddressError: If the postal code format is invalid.
        """
        if not re.match(r'^\d{10}$', postal_code):
            raise AddressError(
                message="Invalid postal code format",
                error_type="INVALID_POSTAL_CODE",
                details={"postal_code": postal_code, "expected_format": "10 digits"}
            )

    @staticmethod
    def validate_phone_number(phone_number: str) -> None:
        """
        Validate that a phone number follows an acceptable international format.
        
        Args:
            phone_number (str): The phone number to validate (optional).
            
        Raises:
            AddressError: If the phone number format is invalid.
        """
        if phone_number and not re.match(r'^\+?[\d\s-]{10,}$', phone_number):
            raise AddressError(
                message="Invalid phone number format",
                error_type="INVALID_PHONE_NUMBER",
                details={"phone_number": phone_number, "expected_format": "+XX-XXXXXXXXXX or similar"}
            )

    @staticmethod
    def validate_coordinates(latitude: float | None, longitude: float | None) -> None:
        """
        Validate that geographical coordinates are within valid ranges.
        
        Args:
            latitude (float | None): The latitude coordinate to validate.
            longitude (float | None): The longitude coordinate to validate.
            
        Raises:
            AddressError: If either coordinate is outside valid ranges.
        """
        if latitude is not None and not -90 <= latitude <= 90:
            raise AddressError(
                message="Invalid latitude value",
                error_type="INVALID_COORDINATES",
                details={"latitude": latitude, "valid_range": "[-90, 90]"}
            )
        if longitude is not None and not -180 <= longitude <= 180:
            raise AddressError(
                message="Invalid longitude value",
                error_type="INVALID_COORDINATES",
                details={"longitude": longitude, "valid_range": "[-180, 180]"}
            )