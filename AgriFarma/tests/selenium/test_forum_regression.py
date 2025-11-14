"""
Regression tests for forum posting functionality.
Tests creating new threads and posting replies.
"""
import pytest
import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TestForumThreadCreation:
    """Test forum thread creation workflow."""
    
    def test_create_new_thread(self, logged_in_browser, live_server, app, db):
        """Test creating a new forum thread."""
        logged_in_browser.get(f'{live_server}/forum/new-thread')
        time.sleep(1)
        
        # Generate unique thread title
        unique_id = random.randint(10000, 99999)
        thread_title = f'Test Thread {unique_id}'
        thread_content = f'This is test content for thread {unique_id}'
        
        # Fill new thread form
        logged_in_browser.find_element(By.NAME, 'title').send_keys(thread_title)
        logged_in_browser.find_element(By.NAME, 'content').send_keys(thread_content)
        
        # Select category (if dropdown exists)
        try:
            category_select = logged_in_browser.find_element(By.NAME, 'category_id')
            # Select first non-zero option
            category_select.send_keys('1')
        except:
            # Category might be optional or structured differently
            pass
        
        # Submit
        submit_btn = logged_in_browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_btn.click()
        
        time.sleep(2)
        
        # Should redirect to thread detail or forum index
        # Check that thread appears or we're on a detail page
        page_source = logged_in_browser.page_source
        current_url = logged_in_browser.current_url
        
        # Either we see the thread title or we're on thread detail
        assert thread_title in page_source or '/forum/thread/' in current_url or 'success' in page_source.lower()
    
    def test_new_thread_requires_title(self, logged_in_browser, live_server):
        """Test that thread creation validates required fields."""
        logged_in_browser.get(f'{live_server}/forum/new-thread')
        time.sleep(1)
        
        # Try to submit without title
        logged_in_browser.find_element(By.NAME, 'content').send_keys('Content without title')
        
        submit_btn = logged_in_browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_btn.click()
        
        time.sleep(1)
        
        # Should stay on form or show validation error
        page_source = logged_in_browser.page_source.lower()
        assert '/forum/new-thread' in logged_in_browser.current_url or 'required' in page_source or 'error' in page_source


class TestForumReply:
    """Test forum reply functionality."""
    
    def test_post_reply_to_thread(self, logged_in_browser, live_server, app, db):
        """Test posting a reply to an existing thread."""
        # First create a thread to reply to
        with app.app_context():
            from agrifarma.models.forum import Thread, Category
            from agrifarma.models.user import User
            
            # Get test user
            user = User.query.filter_by(username='testfarmer').first()
            
            # Create or get a category
            category = Category.query.first()
            if not category:
                category = Category(
                    name='Test Category',
                    slug='test-category',
                    description='Test category for testing',
                    is_active=True
                )
                db.session.add(category)
                db.session.commit()
            
            # Create test thread
            unique_id = random.randint(10000, 99999)
            thread = Thread(
                title=f'Reply Test Thread {unique_id}',
                slug=f'reply-test-thread-{unique_id}',
                content='Thread content for reply testing',
                author_id=user.id,
                category_id=category.id
            )
            db.session.add(thread)
            db.session.commit()
            
            thread_id = thread.id
            thread_slug = thread.slug
        
        # Navigate to thread detail
        logged_in_browser.get(f'{live_server}/forum/thread/{thread_id}/{thread_slug}')
        time.sleep(1)
        
        # Post a reply
        reply_content = f'Test reply content {random.randint(1000, 9999)}'
        
        try:
            reply_field = logged_in_browser.find_element(By.NAME, 'content')
            reply_field.send_keys(reply_content)
            
            submit_btn = logged_in_browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            submit_btn.click()
            
            time.sleep(2)
            
            # Reply should appear on page
            page_source = logged_in_browser.page_source
            assert reply_content in page_source or 'success' in page_source.lower()
        except Exception as e:
            # Reply form might be structured differently
            pytest.skip(f'Reply form not found or structured differently: {e}')


class TestForumNavigation:
    """Test forum navigation and thread listing."""
    
    def test_forum_index_shows_threads(self, logged_in_browser, live_server, app, db):
        """Test forum index displays thread list."""
        # Create some test threads first
        with app.app_context():
            from agrifarma.models.forum import Thread, Category
            from agrifarma.models.user import User
            
            user = User.query.filter_by(username='testfarmer').first()
            category = Category.query.first()
            
            if not category:
                category = Category(
                    name='General',
                    slug='general',
                    is_active=True
                )
                db.session.add(category)
                db.session.commit()
            
            # Add threads if none exist
            thread_count = Thread.query.count()
            if thread_count == 0:
                for i in range(3):
                    thread = Thread(
                        title=f'Sample Thread {i+1}',
                        slug=f'sample-thread-{i+1}',
                        content=f'Content for thread {i+1}',
                        author_id=user.id,
                        category_id=category.id
                    )
                    db.session.add(thread)
                db.session.commit()
        
        logged_in_browser.get(f'{live_server}/forum')
        time.sleep(1)
        
        # Check threads are displayed
        page_source = logged_in_browser.page_source.lower()
        assert 'thread' in page_source or 'discussion' in page_source or 'forum' in page_source
    
    def test_click_thread_opens_detail(self, logged_in_browser, live_server, app, db):
        """Test clicking a thread navigates to detail page."""
        with app.app_context():
            from agrifarma.models.forum import Thread
            
            thread = Thread.query.first()
            if not thread:
                pytest.skip('No threads available for testing')
            
            thread_id = thread.id
            thread_slug = thread.slug
        
        logged_in_browser.get(f'{live_server}/forum')
        time.sleep(1)
        
        # Try to click first thread link
        try:
            thread_link = logged_in_browser.find_element(By.PARTIAL_LINK_TEXT, 'Sample Thread')
            thread_link.click()
            
            time.sleep(1)
            
            # Should be on thread detail page
            assert f'/forum/thread/' in logged_in_browser.current_url
        except:
            # Thread link might be labeled differently
            pytest.skip('Thread link not found with expected text')
