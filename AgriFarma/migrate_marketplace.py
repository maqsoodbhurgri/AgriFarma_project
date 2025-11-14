from agrifarma import create_app
from agrifarma.extensions import db

app = create_app()

with app.app_context():
    db.create_all()
    print("✓ Ensured marketplace tables exist (products, orders, order_items)")
