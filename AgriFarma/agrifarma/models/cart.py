"""CartItem model for persistent user carts.
Session cart is primary for anonymous users; when authenticated we also persist
items so users can recover their cart across devices.
"""
from agrifarma.extensions import db
from agrifarma.models.base import BaseModel


class CartItem(BaseModel):
    __tablename__ = 'cart_items'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)

    # Relationships
    user = db.relationship('User', backref='cart_items')
    product = db.relationship('Product', backref='cart_entries')

    def __repr__(self):
        return f'<CartItem user={self.user_id} product={self.product_id} qty={self.quantity}>'

    def set_quantity(self, qty: int):
        """Safely set quantity with minimum/maximum constraints."""
        qty = max(0, min(int(qty), 100))
        if qty == 0:
            db.session.delete(self)
        else:
            self.quantity = qty
        db.session.commit()
