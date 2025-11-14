"""
Smoke tests for key page loads and element visibility.
Validates that pages load successfully and critical elements are present.
"""
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TestSmokePages:
    """Smoke tests for page accessibility and basic rendering."""
    
    def test_login_page_loads(self, browser, live_server):
        """Test login page loads with form elements."""
        browser.get(f'{live_server}/auth/login')
        
        assert 'Login' in browser.title or 'AgriFarma' in browser.title
        
        # Check form elements present
        username_field = browser.find_element(By.NAME, 'username')
        password_field = browser.find_element(By.NAME, 'password')
        submit_btn = browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        
        assert username_field.is_displayed()
        assert password_field.is_displayed()
        assert submit_btn.is_displayed()
    
    def test_register_page_loads(self, browser, live_server):
        """Test register page loads with form elements."""
        browser.get(f'{live_server}/auth/register')
        
        assert 'Register' in browser.title or 'AgriFarma' in browser.title
        
        # Check key registration fields
        name_field = browser.find_element(By.NAME, 'name')
        username_field = browser.find_element(By.NAME, 'username')
        email_field = browser.find_element(By.NAME, 'email')
        password_field = browser.find_element(By.NAME, 'password')
        
        assert name_field.is_displayed()
        assert username_field.is_displayed()
        assert email_field.is_displayed()
        assert password_field.is_displayed()
    
    def test_forum_index_loads(self, browser, live_server):
        """Test forum index page loads."""
        browser.get(f'{live_server}/forum')
        
        assert 'Forum' in browser.title or 'Discussion' in browser.page_source or 'AgriFarma' in browser.title
        
        # Check for new thread button or forum content
        page_source = browser.page_source.lower()
        assert 'forum' in page_source or 'thread' in page_source or 'discussion' in page_source
    
    def test_marketplace_index_loads(self, browser, live_server):
        """Test marketplace index page loads."""
        browser.get(f'{live_server}/marketplace')
        
        assert 'Marketplace' in browser.title or 'AgriFarma' in browser.title
        
        # Check marketplace-related content
        page_source = browser.page_source.lower()
        assert 'marketplace' in page_source or 'product' in page_source
    
    def test_consultants_index_loads(self, browser, live_server):
        """Test consultants listing page loads."""
        browser.get(f'{live_server}/consultancy/consultants')
        
        assert 'Consultant' in browser.title or 'AgriFarma' in browser.title
        
        # Check consultant-related content
        page_source = browser.page_source.lower()
        assert 'consultant' in page_source or 'consultancy' in page_source
    
    def test_blog_index_loads(self, browser, live_server):
        """Test blog/knowledge base index page loads."""
        browser.get(f'{live_server}/blog')
        
        assert 'Knowledge' in browser.title or 'Blog' in browser.title or 'AgriFarma' in browser.title
        
        # Check blog-related content
        page_source = browser.page_source.lower()
        assert 'knowledge' in page_source or 'blog' in page_source or 'article' in page_source
    
    def test_dashboard_requires_login(self, browser, live_server):
        """Test dashboard redirects to login when not authenticated."""
        browser.get(f'{live_server}/dashboard')
        
        # Should redirect to login
        assert '/auth/login' in browser.current_url or 'login' in browser.page_source.lower()
    
    def test_dashboard_loads_after_login(self, logged_in_browser, live_server):
        """Test dashboard loads for authenticated user."""
        logged_in_browser.get(f'{live_server}/dashboard')
        
        assert 'Dashboard' in logged_in_browser.title or 'AgriFarma' in logged_in_browser.title
        
        # Check dashboard cards/content
        page_source = logged_in_browser.page_source.lower()
        assert 'dashboard' in page_source or 'forum' in page_source or 'marketplace' in page_source


class TestSmokeNavigation:
    """Smoke tests for navigation elements."""
    
    def test_navbar_present_on_pages(self, browser, live_server):
        """Test navbar/sidebar is present on main pages."""
        pages = [
            f'{live_server}/auth/login',
            f'{live_server}/forum',
            f'{live_server}/marketplace',
            f'{live_server}/blog',
        ]
        
        for page_url in pages:
            browser.get(page_url)
            
            # Check for nav elements (navbar or sidebar links)
            page_source = browser.page_source.lower()
            # At minimum, should have some navigation structure
            assert 'nav' in page_source or 'menu' in page_source or 'href' in page_source
    
    def test_footer_or_branding_present(self, browser, live_server):
        """Test AgriFarma branding appears on pages."""
        browser.get(f'{live_server}/auth/login')
        
        page_source = browser.page_source
        assert 'AgriFarma' in page_source or 'agrifarma' in page_source.lower()
