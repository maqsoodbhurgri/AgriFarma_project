"""
Pytest configuration and shared fixtures for Selenium tests.
Provides Flask app, test client, and browser fixtures.
"""
import os
import pytest
import threading
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager

from agrifarma import create_app
from agrifarma.extensions import db as _db
from agrifarma.models.user import User
from agrifarma.models.role import Role


@pytest.fixture(scope='session')
def app():
    """Create Flask app with testing config."""
    app = create_app('testing')
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for easier form testing
    app.config['SERVER_NAME'] = 'localhost:5555'
    
    with app.app_context():
        _db.create_all()
        
        # Create roles if they don't exist
        roles = ['admin', 'farmer', 'consultant', 'vendor']
        for role_name in roles:
            if not Role.query.filter_by(name=role_name).first():
                role = Role(name=role_name, description=f'{role_name.capitalize()} role')
                _db.session.add(role)
        _db.session.commit()
        
        # Create test users
        admin_role = Role.query.filter_by(name='admin').first()
        farmer_role = Role.query.filter_by(name='farmer').first()
        
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                name='Admin User',
                email='admin@test.com',
                mobile='1234567890',
                city='Test City',
                role_id=admin_role.id,
                is_active=True
            )
            admin.set_password('admin123')
            _db.session.add(admin)
        
        if not User.query.filter_by(username='testfarmer').first():
            farmer = User(
                username='testfarmer',
                name='Test Farmer',
                email='farmer@test.com',
                mobile='0987654321',
                city='Farm City',
                role_id=farmer_role.id,
                is_active=True
            )
            farmer.set_password('farmer123')
            _db.session.add(farmer)
        
        _db.session.commit()
    
    yield app
    
    with app.app_context():
        _db.drop_all()


@pytest.fixture(scope='session')
def db(app):
    """Provide database instance."""
    return _db


@pytest.fixture(scope='function')
def client(app):
    """Provide test client for each test."""
    return app.test_client()


@pytest.fixture(scope='session')
def live_server(app):
    """Run Flask app in background thread for Selenium tests."""
    def run_app():
        app.run(host='127.0.0.1', port=5555, use_reloader=False, threaded=True)
    
    thread = threading.Thread(target=run_app, daemon=True)
    thread.start()
    
    # Wait for server to be ready
    time.sleep(2)
    
    yield 'http://localhost:5555'
    
    # Thread will be cleaned up automatically (daemon)


@pytest.fixture(scope='function')
def browser(live_server):
    """Provide headless Chrome WebDriver for each test."""
    chrome_options = ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.implicitly_wait(10)
    
    yield driver
    
    driver.quit()


@pytest.fixture(scope='function')
def logged_in_browser(browser, live_server, app):
    """Provide browser with pre-authenticated farmer user."""
    browser.get(f'{live_server}/auth/login')
    
    # Fill login form
    username_input = browser.find_element('name', 'username')
    password_input = browser.find_element('name', 'password')
    
    username_input.send_keys('testfarmer')
    password_input.send_keys('farmer123')
    
    # Submit
    submit_btn = browser.find_element('css selector', 'button[type="submit"]')
    submit_btn.click()
    
    time.sleep(1)
    
    yield browser


@pytest.fixture(scope='function')
def admin_browser(browser, live_server, app):
    """Provide browser with pre-authenticated admin user."""
    browser.get(f'{live_server}/auth/login')
    
    # Fill login form
    username_input = browser.find_element('name', 'username')
    password_input = browser.find_element('name', 'password')
    
    username_input.send_keys('admin')
    password_input.send_keys('admin123')
    
    # Submit
    submit_btn = browser.find_element('css selector', 'button[type="submit"]')
    submit_btn.click()
    
    time.sleep(1)
    
    yield browser
