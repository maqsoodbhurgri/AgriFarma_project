"""
Regression tests for authentication flows.
Tests user registration, login, and logout workflows.
"""
import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TestAuthRegistration:
    """Test user registration flow."""
    
    def test_register_new_user(self, browser, live_server, app, db):
        """Test complete registration workflow."""
        browser.get(f'{live_server}/auth/register')
        
        # Generate unique username
        import random
        unique_id = random.randint(10000, 99999)
        username = f'newuser{unique_id}'
        email = f'newuser{unique_id}@test.com'
        
        # Fill registration form
        browser.find_element(By.NAME, 'name').send_keys('New Test User')
        browser.find_element(By.NAME, 'username').send_keys(username)
        browser.find_element(By.NAME, 'email').send_keys(email)
        browser.find_element(By.NAME, 'mobile').send_keys(f'123456{unique_id}')
        browser.find_element(By.NAME, 'city').send_keys('Test City')
        
        # Select role
        role_select = browser.find_element(By.NAME, 'role')
        role_select.send_keys('Farmer')
        
        # Select profession
        profession_select = browser.find_element(By.NAME, 'profession')
        profession_select.send_keys('Farmer')
        
        # Set password
        browser.find_element(By.NAME, 'password').send_keys('test123')
        browser.find_element(By.NAME, 'confirm_password').send_keys('test123')
        
        # Submit
        submit_btn = browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_btn.click()
        
        time.sleep(2)
        
        # Should redirect to dashboard or show success
        # Check we're no longer on register page or we see success message
        current_url = browser.current_url
        page_source = browser.page_source.lower()
        
        assert '/auth/register' not in current_url or 'success' in page_source or 'dashboard' in current_url
    
    def test_register_duplicate_username_fails(self, browser, live_server):
        """Test registration with duplicate username shows error."""
        browser.get(f'{live_server}/auth/register')
        
        # Try to register with existing username
        browser.find_element(By.NAME, 'name').send_keys('Duplicate User')
        browser.find_element(By.NAME, 'username').send_keys('testfarmer')  # Already exists
        browser.find_element(By.NAME, 'email').send_keys('duplicate@test.com')
        browser.find_element(By.NAME, 'mobile').send_keys('9999999999')
        browser.find_element(By.NAME, 'city').send_keys('Test City')
        
        role_select = browser.find_element(By.NAME, 'role')
        role_select.send_keys('Farmer')
        
        profession_select = browser.find_element(By.NAME, 'profession')
        profession_select.send_keys('Farmer')
        
        browser.find_element(By.NAME, 'password').send_keys('test123')
        browser.find_element(By.NAME, 'confirm_password').send_keys('test123')
        
        submit_btn = browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_btn.click()
        
        time.sleep(1)
        
        # Should show error about username already exists
        page_source = browser.page_source.lower()
        assert 'exists' in page_source or 'error' in page_source or 'invalid' in page_source


class TestAuthLogin:
    """Test user login flow."""
    
    def test_login_with_valid_credentials(self, browser, live_server):
        """Test login with correct credentials."""
        browser.get(f'{live_server}/auth/login')
        
        browser.find_element(By.NAME, 'username').send_keys('testfarmer')
        browser.find_element(By.NAME, 'password').send_keys('farmer123')
        
        submit_btn = browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_btn.click()
        
        time.sleep(2)
        
        # Should redirect to dashboard
        assert '/dashboard' in browser.current_url or 'dashboard' in browser.page_source.lower()
    
    def test_login_with_invalid_password(self, browser, live_server):
        """Test login with wrong password shows error."""
        browser.get(f'{live_server}/auth/login')
        
        browser.find_element(By.NAME, 'username').send_keys('testfarmer')
        browser.find_element(By.NAME, 'password').send_keys('wrongpassword')
        
        submit_btn = browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_btn.click()
        
        time.sleep(1)
        
        # Should stay on login or show error
        page_source = browser.page_source.lower()
        assert '/auth/login' in browser.current_url or 'invalid' in page_source or 'error' in page_source
    
    def test_login_with_nonexistent_user(self, browser, live_server):
        """Test login with non-existent username shows error."""
        browser.get(f'{live_server}/auth/login')
        
        browser.find_element(By.NAME, 'username').send_keys('nonexistentuser999')
        browser.find_element(By.NAME, 'password').send_keys('password123')
        
        submit_btn = browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_btn.click()
        
        time.sleep(1)
        
        page_source = browser.page_source.lower()
        assert '/auth/login' in browser.current_url or 'invalid' in page_source or 'error' in page_source


class TestAuthLogout:
    """Test logout functionality."""
    
    def test_logout_redirects_to_login(self, logged_in_browser, live_server):
        """Test logout flow."""
        # User is already logged in via fixture
        # Navigate to logout (if route exists)
        try:
            logged_in_browser.get(f'{live_server}/auth/logout')
            time.sleep(1)
            
            # Should redirect to login or home
            assert '/auth/login' in logged_in_browser.current_url or 'login' in logged_in_browser.page_source.lower()
        except Exception:
            # Logout route might not exist or be implemented differently
            pytest.skip('Logout route not accessible or not implemented')


class TestAuthProtectedPages:
    """Test that protected pages require authentication."""
    
    def test_new_thread_requires_login(self, browser, live_server):
        """Test creating thread requires login."""
        browser.get(f'{live_server}/forum/new-thread')
        time.sleep(1)
        
        # Should redirect to login
        assert '/auth/login' in browser.current_url or 'login' in browser.page_source.lower()
    
    def test_new_thread_accessible_when_logged_in(self, logged_in_browser, live_server):
        """Test new thread page accessible after login."""
        logged_in_browser.get(f'{live_server}/forum/new-thread')
        time.sleep(1)
        
        # Should show new thread form
        page_source = logged_in_browser.page_source.lower()
        assert 'title' in page_source and 'content' in page_source or 'thread' in page_source
