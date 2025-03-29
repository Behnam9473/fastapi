from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from database import Base
from utils.exceptions import AddressError
import re


class Address(Base):
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
        """Validate postal code format"""
        if not re.match(r'^\d{10}$', postal_code):
            raise AddressError(
                message="Invalid postal code format",
                error_type="INVALID_POSTAL_CODE",
                details={"postal_code": postal_code, "expected_format": "10 digits"}
            )

    @staticmethod
    def validate_phone_number(phone_number: str) -> None:
        """Validate phone number format if provided"""
        if phone_number and not re.match(r'^\+?[\d\s-]{10,}$', phone_number):
            raise AddressError(
                message="Invalid phone number format",
                error_type="INVALID_PHONE_NUMBER",
                details={"phone_number": phone_number, "expected_format": "+XX-XXXXXXXXXX or similar"}
            )

    @staticmethod
    def validate_coordinates(latitude: float | None, longitude: float | None) -> None:
        """Validate geographical coordinates if provided"""
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