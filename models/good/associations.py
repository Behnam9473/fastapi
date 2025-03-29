from sqlalchemy import Table, Column, Integer, ForeignKey
from database import Base

good_color_association = Table(
    "good_color_association",
    Base.metadata,
    Column("good_id", Integer, ForeignKey("good.id", ondelete="CASCADE")),
    Column("color_id", Integer, ForeignKey("color.id", ondelete="CASCADE"))
)
