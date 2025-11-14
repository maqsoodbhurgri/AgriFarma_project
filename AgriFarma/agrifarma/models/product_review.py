"""Product review model for marketplace."""
from agrifarma.extensions import db
from agrifarma.models.base import BaseModel

class ProductReview(BaseModel):
    __tablename__ = 'product_reviews'

    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    comment = db.Column(db.Text)

    # Relationships
    product = db.relationship('Product', backref='reviews')
    user = db.relationship('User', backref='product_reviews')

    def __repr__(self):
        return f'<ProductReview product={self.product_id} user={self.user_id} rating={self.rating}>'
