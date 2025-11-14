"""
Product model for e-commerce marketplace.
"""
from datetime import datetime
from agrifarma.extensions import db
from agrifarma.models.base import BaseModel


class Product(BaseModel):
    """
    Product model for marketplace items.
    Tracks inventory, pricing, and categorization.
    """
    __tablename__ = 'products'
    
    # Basic Information
    name = db.Column(db.String(200), nullable=False, index=True)
    slug = db.Column(db.String(250), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    
    # Categorization
    category = db.Column(db.String(100), nullable=False, index=True)  # Seeds, Fertilizers, Tools, etc.
    subcategory = db.Column(db.String(100))
    
    # Pricing
    price = db.Column(db.Float, nullable=False)
    original_price = db.Column(db.Float)  # For discount calculation
    currency = db.Column(db.String(10), default='PKR')
    
    # Inventory
    stock_quantity = db.Column(db.Integer, default=0, nullable=False)
    low_stock_threshold = db.Column(db.Integer, default=10)
    sku = db.Column(db.String(100), unique=True)  # Stock Keeping Unit
    
    # Product Details
    unit = db.Column(db.String(50))  # kg, liter, piece, bag, etc.
    weight = db.Column(db.Float)  # in kg
    brand = db.Column(db.String(100))
    manufacturer = db.Column(db.String(150))
    
    # Media
    image_url = db.Column(db.String(255))
    images = db.Column(db.JSON)  # Array of image URLs
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    in_stock = db.Column(db.Boolean, default=True)
    
    # Vendor Information
    vendor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Statistics
    view_count = db.Column(db.Integer, default=0)
    sold_count = db.Column(db.Integer, default=0)
    rating = db.Column(db.Float, default=0.0)
    review_count = db.Column(db.Integer, default=0)
    
    # SEO
    meta_title = db.Column(db.String(200))
    meta_description = db.Column(db.String(300))
    meta_keywords = db.Column(db.String(255))
    
    # Relationships
    vendor = db.relationship('User', backref='products', lazy=True)
    order_items = db.relationship('OrderItem', backref='product', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Product {self.name}>'
    
    def is_low_stock(self):
        """Check if product stock is below threshold."""
        return self.stock_quantity <= self.low_stock_threshold
    
    def get_discount_percentage(self):
        """Calculate discount percentage if original price exists."""
        if self.original_price and self.original_price > self.price:
            return round(((self.original_price - self.price) / self.original_price) * 100, 2)
        return 0
    
    def update_stock(self, quantity_change):
        """Update stock quantity."""
        self.stock_quantity += quantity_change
        self.in_stock = self.stock_quantity > 0
        db.session.commit()
    
    def increment_views(self):
        """Increment product view count."""
        self.view_count += 1
        db.session.commit()
    
    def increment_sold(self, quantity=1):
        """Increment sold count."""
        self.sold_count += quantity
        db.session.commit()


class Order(BaseModel):
    """
    Order model for tracking customer purchases.
    """
    __tablename__ = 'orders'
    
    # Order Identification
    order_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    
    # Customer Information
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Order Details
    total_amount = db.Column(db.Float, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)
    tax_amount = db.Column(db.Float, default=0.0)
    shipping_fee = db.Column(db.Float, default=0.0)
    discount_amount = db.Column(db.Float, default=0.0)
    
    # Status
    status = db.Column(db.String(50), default='pending', nullable=False)  # pending, processing, shipped, delivered, cancelled
    payment_status = db.Column(db.String(50), default='unpaid')  # unpaid, paid, refunded
    payment_method = db.Column(db.String(50))  # cod, bank_transfer, card, etc.
    
    # Shipping Information
    shipping_name = db.Column(db.String(150))
    shipping_address = db.Column(db.Text)
    shipping_city = db.Column(db.String(100))
    shipping_state = db.Column(db.String(100))
    shipping_postal_code = db.Column(db.String(20))
    shipping_phone = db.Column(db.String(20))
    
    # Tracking
    tracking_number = db.Column(db.String(100))
    carrier = db.Column(db.String(100))
    
    # Timestamps
    order_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    paid_at = db.Column(db.DateTime)
    shipped_at = db.Column(db.DateTime)
    delivered_at = db.Column(db.DateTime)
    cancelled_at = db.Column(db.DateTime)
    
    # Notes
    customer_notes = db.Column(db.Text)
    admin_notes = db.Column(db.Text)
    
    # Relationships
    customer = db.relationship('User', backref='orders', lazy=True)
    order_items = db.relationship('OrderItem', backref='order', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Order {self.order_number}>'
    
    def get_item_count(self):
        """Get total number of items in order."""
        return sum(item.quantity for item in self.order_items)
    
    def update_status(self, new_status):
        """Update order status with timestamp."""
        self.status = new_status
        
        if new_status == 'paid' and not self.paid_at:
            self.paid_at = datetime.utcnow()
        elif new_status == 'shipped' and not self.shipped_at:
            self.shipped_at = datetime.utcnow()
        elif new_status == 'delivered' and not self.delivered_at:
            self.delivered_at = datetime.utcnow()
        elif new_status == 'cancelled' and not self.cancelled_at:
            self.cancelled_at = datetime.utcnow()
        
        db.session.commit()


class OrderItem(BaseModel):
    """
    Order line items - individual products in an order.
    """
    __tablename__ = 'order_items'
    
    # Foreign Keys
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    
    # Item Details
    product_name = db.Column(db.String(200), nullable=False)  # Store name at time of order
    product_sku = db.Column(db.String(100))
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    
    # Discount (if any)
    discount_percent = db.Column(db.Float, default=0.0)
    discount_amount = db.Column(db.Float, default=0.0)
    
    def __repr__(self):
        return f'<OrderItem {self.product_name} x{self.quantity}>'
