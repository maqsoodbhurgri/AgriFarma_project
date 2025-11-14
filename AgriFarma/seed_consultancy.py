from datetime import datetime, timedelta
from agrifarma import create_app
from agrifarma.extensions import db
from agrifarma.models.role import Role
from agrifarma.models.user import User
from agrifarma.models.consultancy import ConsultantProfile, ConsultationSlot

app = create_app()

with app.app_context():
    # Ensure roles
    consultant_role = Role.query.filter_by(name='consultant').first()
    if not consultant_role:
        consultant_role = Role(name='consultant', description='Consultant')
        db.session.add(consultant_role)
        db.session.flush()

    # Create consultant user if not exists
    user = User.query.filter_by(username='consultant1').first()
    if not user:
        user = User(username='consultant1', name='Dr. Soil Expert', email='consult1@example.com', role_id=consultant_role.id,
                    city='Hyderabad', state='Sindh', country='Pakistan', profession='consultant', expertise_level='expert')
        user.set_password('password123')
        db.session.add(user)
        db.session.flush()

    # Create profile
    profile = ConsultantProfile.query.filter_by(user_id=user.id).first()
    if not profile:
        profile = ConsultantProfile(user_id=user.id, specialization='Soil & Irrigation', bio='10+ years advising farmers.', hourly_rate=1500.0, is_verified=True)
        db.session.add(profile)
        db.session.flush()

    # Create a few future slots
    now = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
    created = 0
    for days in range(1, 6):
        start = now + timedelta(days=days, hours=10)
        end = start + timedelta(minutes=45)
        exists = ConsultationSlot.query.filter_by(consultant_profile_id=profile.id, start_time=start).first()
        if not exists:
            db.session.add(ConsultationSlot(consultant_profile_id=profile.id, start_time=start, end_time=end, status='available', price=1500.0))
            created += 1
    db.session.commit()
    print(f"✓ Seeded consultant profile and {created} slots for user {user.username}")
