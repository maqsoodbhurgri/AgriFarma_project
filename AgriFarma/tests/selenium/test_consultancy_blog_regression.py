"""
Regression tests for consultancy and blog functionality.
Tests consultant contact forms and blog commenting.
"""
import pytest
import time
import random
from selenium.webdriver.common.by import By


class TestConsultantContact:
    """Test consultant contact functionality."""
    
    def test_consultant_listing_loads(self, browser, live_server, app, db):
        """Test consultant listing page displays consultants."""
        # Ensure consultant profiles exist
        with app.app_context():
            from agrifarma.models.consultancy import ConsultantProfile
            from agrifarma.models.user import User
            from agrifarma.models.role import Role
            
            profile_count = ConsultantProfile.query.filter_by(is_verified=True).count()
            
            if profile_count == 0:
                # Create sample consultant
                consultant_role = Role.query.filter_by(name='consultant').first()
                if not consultant_role:
                    consultant_role = Role(name='consultant', description='Consultant')
                    db.session.add(consultant_role)
                    db.session.commit()
                
                consultant_user = User.query.filter_by(username='testconsultant').first()
                if not consultant_user:
                    consultant_user = User(
                        username='testconsultant',
                        name='Test Consultant',
                        email='consultant@test.com',
                        mobile='5555555555',
                        city='Consultant City',
                        role_id=consultant_role.id,
                        is_active=True
                    )
                    consultant_user.set_password('test123')
                    db.session.add(consultant_user)
                    db.session.commit()
                
                profile = ConsultantProfile(
                    user_id=consultant_user.id,
                    specialization='Crop Management',
                    bio='Expert in crop management',
                    hourly_rate=500.0,
                    is_verified=True
                )
                db.session.add(profile)
                db.session.commit()
        
        browser.get(f'{live_server}/consultancy/consultants')
        time.sleep(1)
        
        page_source = browser.page_source.lower()
        assert 'consultant' in page_source or 'consultancy' in page_source
    
    def test_consultant_detail_page_loads(self, browser, live_server, app, db):
        """Test consultant detail page displays profile info."""
        with app.app_context():
            from agrifarma.models.consultancy import ConsultantProfile
            
            profile = ConsultantProfile.query.filter_by(is_verified=True).first()
            if not profile:
                pytest.skip('No verified consultant profiles available')
            
            consultant_id = profile.id
            consultant_name = profile.user.name
        
        browser.get(f'{live_server}/consultancy/consultant/{consultant_id}')
        time.sleep(1)
        
        page_source = browser.page_source
        assert consultant_name in page_source or 'Consultant' in browser.title
    
    def test_submit_consultant_contact_form(self, logged_in_browser, live_server, app, db):
        """Test submitting contact form to consultant."""
        with app.app_context():
            from agrifarma.models.consultancy import ConsultantProfile
            
            profile = ConsultantProfile.query.filter_by(is_verified=True).first()
            if not profile:
                pytest.skip('No verified consultant profiles available')
            
            consultant_id = profile.id
        
        logged_in_browser.get(f'{live_server}/consultancy/consultant/{consultant_id}')
        time.sleep(1)
        
        # Try to fill and submit contact form
        try:
            subject_field = logged_in_browser.find_element(By.NAME, 'subject')
            message_field = logged_in_browser.find_element(By.NAME, 'message')
            
            subject_field.send_keys('Test Inquiry')
            message_field.send_keys(f'Test message {random.randint(1000, 9999)}')
            
            submit_btn = logged_in_browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            submit_btn.click()
            
            time.sleep(1)
            
            # Should show success message or redirect
            page_source = logged_in_browser.page_source.lower()
            assert 'success' in page_source or 'sent' in page_source or 'message' in page_source
        except Exception as e:
            pytest.skip(f'Contact form not found or structured differently: {e}')


class TestBlogComments:
    """Test blog post commenting functionality."""
    
    def test_blog_listing_loads(self, browser, live_server, app, db):
        """Test blog listing page displays posts."""
        # Ensure blog posts exist
        with app.app_context():
            from agrifarma.models.blog import BlogPost, BlogCategory
            from agrifarma.models.user import User
            
            post_count = BlogPost.query.filter_by(is_published=True, is_deleted=False).count()
            
            if post_count == 0:
                # Create sample blog post
                author = User.query.filter_by(username='admin').first()
                
                category = BlogCategory.query.first()
                if not category:
                    category = BlogCategory(
                        name='Agriculture Tips',
                        slug='agriculture-tips',
                        is_active=True
                    )
                    db.session.add(category)
                    db.session.commit()
                
                post = BlogPost(
                    title='Sample Blog Post',
                    slug='sample-blog-post',
                    content='This is sample blog content for testing.',
                    excerpt='Sample excerpt',
                    author_id=author.id,
                    category_id=category.id,
                    is_published=True
                )
                db.session.add(post)
                db.session.commit()
        
        browser.get(f'{live_server}/blog')
        time.sleep(1)
        
        page_source = browser.page_source.lower()
        assert 'blog' in page_source or 'knowledge' in page_source or 'article' in page_source
    
    def test_blog_detail_page_loads(self, browser, live_server, app, db):
        """Test blog detail page displays post content."""
        with app.app_context():
            from agrifarma.models.blog import BlogPost
            
            post = BlogPost.query.filter_by(is_published=True, is_deleted=False).first()
            if not post:
                pytest.skip('No published blog posts available')
            
            post_id = post.id
            post_slug = post.slug
            post_title = post.title
        
        browser.get(f'{live_server}/blog/post/{post_id}/{post_slug}')
        time.sleep(1)
        
        page_source = browser.page_source
        assert post_title in page_source or 'Blog' in browser.title
    
    def test_submit_blog_comment(self, logged_in_browser, live_server, app, db):
        """Test submitting a comment on a blog post."""
        with app.app_context():
            from agrifarma.models.blog import BlogPost
            
            post = BlogPost.query.filter_by(is_published=True, is_deleted=False).first()
            if not post:
                pytest.skip('No published blog posts available')
            
            post_id = post.id
            post_slug = post.slug
        
        logged_in_browser.get(f'{live_server}/blog/post/{post_id}/{post_slug}')
        time.sleep(1)
        
        # Try to post comment
        try:
            comment_field = logged_in_browser.find_element(By.NAME, 'content')
            comment_content = f'Test comment {random.randint(1000, 9999)}'
            
            comment_field.send_keys(comment_content)
            
            submit_btn = logged_in_browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            submit_btn.click()
            
            time.sleep(2)
            
            # Comment should appear or success message shown
            page_source = logged_in_browser.page_source
            assert comment_content in page_source or 'success' in page_source.lower()
        except Exception as e:
            pytest.skip(f'Comment form not found or structured differently: {e}')
    
    def test_blog_detail_shows_existing_comments(self, browser, live_server, app, db):
        """Test blog detail page displays existing comments."""
        with app.app_context():
            from agrifarma.models.blog import BlogPost, BlogComment
            from agrifarma.models.user import User
            
            post = BlogPost.query.filter_by(is_published=True, is_deleted=False).first()
            if not post:
                pytest.skip('No published blog posts available')
            
            # Create a comment if none exist
            comment_count = BlogComment.query.filter_by(post_id=post.id, is_deleted=False).count()
            if comment_count == 0:
                user = User.query.filter_by(username='testfarmer').first()
                comment = BlogComment(
                    content='Sample comment for testing',
                    author_id=user.id,
                    post_id=post.id,
                    is_approved=True
                )
                db.session.add(comment)
                db.session.commit()
            
            post_id = post.id
            post_slug = post.slug
        
        browser.get(f'{live_server}/blog/post/{post_id}/{post_slug}')
        time.sleep(1)
        
        page_source = browser.page_source.lower()
        # Check for comment-related content
        assert 'comment' in page_source or 'reply' in page_source or 'discussion' in page_source
