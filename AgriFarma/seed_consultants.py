"""
Seed script for consultant profiles with distinct images
"""
import os
import random
from agrifarma.extensions import db
from agrifarma.models.user import User
from agrifarma.models.role import Role
from agrifarma.models.consultancy import ConsultantProfile
from app import app

# Sample consultant data
CONSULTANTS = [
    {
        "username": "drkhalid",
        "name": "Dr. Khalid Hussain",
        "email": "khalid.hussain@agrifarma.pk",
        "specialization": "Soil Science",
        "bio": "PhD in Soil Science, 15+ years experience advising farmers on soil health, crop rotation, and sustainable practices.",
        "hourly_rate": 2500,
        "profile_picture": "images/user/avatar-1.jpg"
    },
    {
        "username": "drsamina",
        "name": "Dr. Samina Tariq",
        "email": "samina.tariq@agrifarma.pk",
        "specialization": "Plant Pathology",
        "bio": "Expert in plant diseases, pest management, and crop protection. Regular speaker at agri conferences.",
        "hourly_rate": 2200,
        "profile_picture": "images/user/avatar-2.jpg"
    },
    {
        "username": "engrali",
        "name": "Engr. Ali Raza",
        "email": "ali.raza@agrifarma.pk",
        "specialization": "Irrigation Engineering",
        "bio": "Certified irrigation engineer, specializes in drip and sprinkler systems for water conservation.",
        "hourly_rate": 2000,
        "profile_picture": "images/user/avatar-3.jpg"
    },
    {
        "username": "drfatima",
        "name": "Dr. Fatima Noor",
        "email": "fatima.noor@agrifarma.pk",
        "specialization": "Entomology",
        "bio": "Researcher in insect pest control, IPM, and organic farming. Consults for major agri companies.",
        "hourly_rate": 2100,
        "profile_picture": "images/user/avatar-4.jpg"
    },
    {
        "username": "drusman",
        "name": "Dr. Usman Ghani",
        "email": "usman.ghani@agrifarma.pk",
        "specialization": "Crop Nutrition",
        "bio": "Crop nutritionist with expertise in fertilizer management and micronutrients for high yield.",
        "hourly_rate": 2300,
        "profile_picture": "images/user/avatar-5.jpg"
    },
    {
        "username": "mrsabeer",
        "name": "Ms. Sabeer Ahmed",
        "email": "sabeer.ahmed@agrifarma.pk",
        "specialization": "Agri Business",
        "bio": "Agri business consultant, helps farmers with market access, value addition, and agri startups.",
        "hourly_rate": 1800,
        "profile_picture": "images/user/avatar-6.jpg"
    }
]

def seed_consultants():
    with app.app_context():
        consultant_role = Role.query.filter_by(name="consultant").first()
        for c in CONSULTANTS:
            user = User.query.filter_by(email=c["email"]).first()
            if not user:
                user = User(
                    username=c["username"],
                    name=c["name"],
                    email=c["email"],
                    password_hash=User.generate_password_hash("consultant123"),
                    role=consultant_role,
                    profession="consultant",
                    expertise_level="expert",
                    specialization=c["specialization"],
                    bio=c["bio"],
                    profile_picture=c["profile_picture"],
                    is_active=True,
                    is_verified=True,
                    city=random.choice(["Lahore", "Karachi", "Faisalabad", "Multan", "Hyderabad"]),
                    country="Pakistan"
                )
                db.session.add(user)
                db.session.flush()  # get user.id
            profile = ConsultantProfile.query.filter_by(user_id=user.id).first()
            if not profile:
                profile = ConsultantProfile(
                    user_id=user.id,
                    specialization=c["specialization"],
                    bio=c["bio"],
                    hourly_rate=c["hourly_rate"],
                    rating=round(random.uniform(4.2, 5.0), 2),
                    total_sessions=random.randint(20, 200),
                    is_verified=True,
                    available_online=True
                )
                db.session.add(profile)
        db.session.commit()
        print("Consultant profiles seeded successfully.")

if __name__ == "__main__":
    seed_consultants()
