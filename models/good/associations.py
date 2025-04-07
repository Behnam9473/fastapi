from sqlalchemy import Table, Column, Integer, ForeignKey
from database import Base

good_color_association = Table(
    "good_color_association",
    Base.metadata,
    Column("good_id", Integer, ForeignKey("good.id", ondelete="CASCADE")),
    Column("color_id", Integer, ForeignKey("color.id", ondelete="CASCADE"))
)
"""
Association table for many-to-many relationship between goods and colors.

This table establishes a relationship where:
- A good can have multiple colors
- A color can be associated with multiple goods

Columns:
- good_id: Foreign key referencing the id column in the good table
- color_id: Foreign key referencing the id column in the color table

Both foreign keys are configured with CASCADE on delete, meaning when a good or color
is deleted, all its associations will be automatically deleted as well.
"""
