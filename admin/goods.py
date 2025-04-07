from sqladmin import Admin, ModelView
from models.good.goods import Good, Category, Attribute
from models.good.colors import Color
from models.good.ratings import ProductRating

class GoodAdmin(ModelView, model=Good):
    """
    Admin interface for managing Goods in the database.
    
    Attributes:
        column_list: List of columns to display in admin interface
        column_searchable_list: List of searchable columns
        column_sortable_list: List of sortable columns
        column_formatters: Formatting for datetime columns
        form_excluded_columns: Columns excluded from forms
    """
    column_list = [
        "id", "name", "sku", "status", "category.name", 
        "is_validated", "weight", "created_at", "updated_at"
    ]
    column_searchable_list = ["name", "sku", "status"]
    column_sortable_list = ["id", "name", "created_at", "updated_at"]
    column_formatters = {
        "created_at": lambda m, a: m.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        "updated_at": lambda m, a: m.updated_at.strftime("%Y-%m-%d %H:%M:%S")
    }
    form_excluded_columns = ["sku", "created_at", "updated_at"]
    
class ColorAdmin(ModelView, model=Color):
    """
    Admin interface for managing Colors in the database.
    
    Currently has no configured columns (column_list is empty).
    """
    column_list = []  
    
class CategoryAdmin(ModelView, model=Category):
    """
    Admin interface for managing Categories in the database.
    
    Currently has no configured columns (column_list is empty).
    """
    column_list = []  
    
class RatingAdmin(ModelView, model=ProductRating):
    """
    Admin interface for managing Product Ratings in the database.
    
    Currently has no configured columns (column_list is empty).
    """
    column_list = []  
    
class AttributeAdmin(ModelView, model=Attribute):
    """
    Admin interface for managing Attributes in the database.
    
    Currently has no configured columns (column_list is empty).
    """
    column_list = []  

def setup_goods_admin(app, engine):
    """
    Configure and register all goods-related admin views.
    
    Args:
        app: FastAPI application instance
        engine: SQLAlchemy engine instance
    
    Returns:
        Admin: Configured admin interface with all goods-related views
    """
    admin = Admin(app, engine)
    admin.add_view(GoodAdmin)
    admin.add_view(ColorAdmin)
    admin.add_view(CategoryAdmin)
    admin.add_view(RatingAdmin)
    admin.add_view(AttributeAdmin)
    return admin