"""
Migration script to create blog tables
"""
from app import app
from agrifarma.extensions import db
from agrifarma.models.blog import BlogCategory, BlogPost, BlogComment, BlogLike

with app.app_context():
    try:
        # Create all blog tables
        db.create_all()
        print("✓ Successfully created blog tables (blog_categories, blog_posts, blog_comments, blog_likes)")
    except Exception as e:
        print(f"✗ Error: {e}")
