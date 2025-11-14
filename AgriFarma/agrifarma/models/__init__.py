"""
Models package initialization.
Imports all models to make them available when importing from agrifarma.models
"""
from agrifarma.models.user import User
from agrifarma.models.role import Role
from agrifarma.models.forum import Category, Thread, Reply
from agrifarma.models.product import Product, Order, OrderItem
from agrifarma.models.cart import CartItem
from agrifarma.models.product_review import ProductReview
from agrifarma.models.consultancy import ConsultantProfile, ConsultationSlot, ConsultationBooking

__all__ = ['User', 'Role', 'Category', 'Thread', 'Reply', 'Product', 'Order', 'OrderItem', 'CartItem',
		   'ConsultantProfile', 'ConsultationSlot', 'ConsultationBooking', 'ProductReview']

