from agrifarma import create_app
from agrifarma.extensions import db
from agrifarma.models.consultancy import ConsultantProfile, ConsultationSlot, ConsultationBooking
from agrifarma.models.product_review import ProductReview

app = create_app()

with app.app_context():
    db.create_all()
    print("✓ Ensured consultancy tables exist (consultant_profiles, consultation_slots, consultation_bookings)")
    print("✓ Ensured product_reviews table exists")
