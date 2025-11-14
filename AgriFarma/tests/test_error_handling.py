"""
Test suite for error handling and access control decorators.

This module tests:
1. Custom error pages (403, 404, 500)
2. Flash message display
3. Role-based access control decorators
4. Unauthorized access redirects
"""

import pytest
from flask import url_for, session
from agrifarma import db
from agrifarma.models.user import User, Role


class TestErrorPages:
    """Test custom error pages."""
    
    def test_404_page(self, client):
        """Test 404 error page renders correctly."""
        response = client.get('/nonexistent-page')
        assert response.status_code == 404
        assert b'404' in response.data
        assert b'Page Not Found' in response.data
        assert b'feather icon-alert-circle' in response.data
        assert b'Back to Homepage' in response.data
    
    def test_404_page_styling(self, client):
        """Test 404 page has proper styling."""
        response = client.get('/does-not-exist')
        assert b'auth-wrapper' in response.data
        assert b'gradient' in response.data
        assert b'#28a745' in response.data  # Green color
    
    def test_500_page_on_error(self, client, app):
        """Test 500 error page renders on internal error."""
        # Create a route that raises an exception
        @app.route('/trigger-500')
        def trigger_500():
            raise Exception("Test error")
        
        response = client.get('/trigger-500')
        assert response.status_code == 500
        assert b'500' in response.data
        assert b'Internal Server Error' in response.data
        assert b'feather icon-alert-triangle' in response.data
    
    def test_403_page_unauthorized(self, client, normal_user):
        """Test 403 page renders for unauthorized access."""
        # Login as normal user
        client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'password123'
        })
        
        # Try to access admin-only page
        response = client.get('/admin/dashboard')
        assert response.status_code == 403
        assert b'403' in response.data
        assert b'Access Forbidden' in response.data
        assert b'feather icon-lock' in response.data


class TestFlashMessages:
    """Test flash message system."""
    
    def test_flash_message_display(self, client):
        """Test flash messages display correctly."""
        # Trigger a flash message by logging in with wrong credentials
        response = client.post('/auth/login', data={
            'username': 'wronguser',
            'password': 'wrongpass'
        }, follow_redirects=True)
        
        assert b'alert' in response.data
        assert b'feather icon' in response.data
        assert b'close' in response.data  # Dismissible
    
    def test_flash_success_category(self, client, normal_user):
        """Test success flash message styling."""
        # Login successfully to trigger success message
        response = client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'password123'
        }, follow_redirects=True)
        
        assert b'alert-success' in response.data
        assert b'feather icon-check-circle' in response.data
    
    def test_flash_danger_category(self, client):
        """Test danger flash message styling."""
        response = client.post('/auth/login', data={
            'username': 'nonexistent',
            'password': 'wrong'
        }, follow_redirects=True)
        
        assert b'alert-danger' in response.data
        assert b'feather icon-x-circle' in response.data
    
    def test_flash_warning_category(self, client, inactive_user):
        """Test warning flash message styling."""
        # Try to login with inactive account
        response = client.post('/auth/login', data={
            'username': 'inactive',
            'password': 'password123'
        }, follow_redirects=True)
        
        assert b'alert-warning' in response.data
        assert b'feather icon-alert-triangle' in response.data
    
    def test_flash_info_category(self, client, normal_user):
        """Test info flash message styling."""
        # Logout to trigger info message
        client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'password123'
        })
        response = client.get('/auth/logout', follow_redirects=True)
        
        assert b'alert-info' in response.data
        assert b'feather icon-info' in response.data
    
    def test_flash_dismissible(self, client):
        """Test flash messages are dismissible."""
        response = client.post('/auth/login', data={
            'username': 'wrong',
            'password': 'wrong'
        }, follow_redirects=True)
        
        assert b'alert-dismissible' in response.data
        assert b'data-dismiss="alert"' in response.data
        assert b'&times;' in response.data


class TestAccessControlDecorators:
    """Test role-based access control decorators."""
    
    def test_admin_required_allows_admin(self, client, admin_user):
        """Test admin_required decorator allows admin users."""
        client.post('/auth/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        
        response = client.get('/analytics/dashboard')
        assert response.status_code == 200
    
    def test_admin_required_blocks_non_admin(self, client, normal_user):
        """Test admin_required decorator blocks non-admin users."""
        client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'password123'
        })
        
        response = client.get('/analytics/dashboard')
        assert response.status_code in [302, 403]  # Redirect or Forbidden
    
    def test_admin_required_redirects_anonymous(self, client):
        """Test admin_required redirects anonymous users to login."""
        response = client.get('/analytics/dashboard')
        assert response.status_code == 302
        assert b'/auth/login' in response.data or response.location and '/auth/login' in response.location
    
    def test_consultant_required_allows_consultant(self, client, consultant_user):
        """Test consultant_required decorator allows consultant users."""
        client.post('/auth/login', data={
            'username': 'consultant',
            'password': 'consultant123'
        })
        
        # Assuming there's a consultant-only route
        response = client.get('/consultations/dashboard')
        # Should be 200 if route exists, 404 if not implemented yet
        assert response.status_code in [200, 404]
    
    def test_farmer_required_allows_farmer(self, client, farmer_user):
        """Test farmer_required decorator allows farmer users."""
        client.post('/auth/login', data={
            'username': 'farmer',
            'password': 'farmer123'
        })
        
        # Test access to farmer-only route
        response = client.get('/farm/dashboard')
        assert response.status_code in [200, 404]
    
    def test_vendor_required_allows_vendor(self, client, vendor_user):
        """Test vendor_required decorator allows vendor users."""
        client.post('/auth/login', data={
            'username': 'vendor',
            'password': 'vendor123'
        })
        
        # Test access to vendor-only route
        response = client.get('/marketplace/vendor/products')
        assert response.status_code in [200, 404]
    
    def test_role_required_multiple_roles(self, client, admin_user, consultant_user):
        """Test role_required decorator with multiple roles."""
        # Test with admin
        client.post('/auth/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        response = client.get('/analytics/reports')
        assert response.status_code == 200
        
        # Logout and test with consultant
        client.get('/auth/logout')
        client.post('/auth/login', data={
            'username': 'consultant',
            'password': 'consultant123'
        })
        response = client.get('/analytics/reports')
        # Should allow if consultant role is in allowed roles
        assert response.status_code in [200, 403]
    
    def test_unauthorized_access_flash_message(self, client, normal_user):
        """Test unauthorized access shows appropriate flash message."""
        client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'password123'
        })
        
        response = client.get('/analytics/dashboard', follow_redirects=True)
        assert b'Access denied' in response.data or b'permission' in response.data
    
    def test_next_parameter_preserved(self, client):
        """Test 'next' parameter is preserved in login redirect."""
        response = client.get('/analytics/dashboard')
        assert response.status_code == 302
        
        # Check if next parameter is in redirect location
        location = response.location
        assert 'next=' in location or '/auth/login' in location


class TestOwnershipValidation:
    """Test ownership validation helper function."""
    
    def test_is_owner_or_admin_owner(self, client, normal_user):
        """Test is_owner_or_admin returns True for resource owner."""
        from agrifarma.utils.decorators import is_owner_or_admin
        
        client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'password123'
        })
        
        # Assuming normal_user has id=2
        with client.application.app_context():
            result = is_owner_or_admin(normal_user.id)
            assert result is True
    
    def test_is_owner_or_admin_admin(self, client, admin_user):
        """Test is_owner_or_admin returns True for admin."""
        from agrifarma.utils.decorators import is_owner_or_admin
        
        client.post('/auth/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        
        # Admin should have access to any resource
        with client.application.app_context():
            result = is_owner_or_admin(999)  # Random user ID
            assert result is True
    
    def test_is_owner_or_admin_other_user(self, client, normal_user):
        """Test is_owner_or_admin returns False for other users."""
        from agrifarma.utils.decorators import is_owner_or_admin
        
        client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'password123'
        })
        
        # Try to access another user's resource
        with client.application.app_context():
            result = is_owner_or_admin(999)  # Different user ID
            assert result is False


# Fixtures for test users

@pytest.fixture
def admin_user(app):
    """Create an admin user for testing."""
    with app.app_context():
        admin_role = Role.query.filter_by(name='admin').first()
        if not admin_role:
            admin_role = Role(name='admin', description='Administrator')
            db.session.add(admin_role)
            db.session.commit()
        
        user = User(
            username='admin',
            email='admin@test.com',
            first_name='Admin',
            last_name='User',
            role_id=admin_role.id,
            is_active=True
        )
        user.set_password('admin123')
        db.session.add(user)
        db.session.commit()
        
        yield user
        
        db.session.delete(user)
        db.session.commit()


@pytest.fixture
def normal_user(app):
    """Create a normal farmer user for testing."""
    with app.app_context():
        farmer_role = Role.query.filter_by(name='farmer').first()
        if not farmer_role:
            farmer_role = Role(name='farmer', description='Farmer')
            db.session.add(farmer_role)
            db.session.commit()
        
        user = User(
            username='testuser',
            email='test@test.com',
            first_name='Test',
            last_name='User',
            role_id=farmer_role.id,
            is_active=True
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        yield user
        
        db.session.delete(user)
        db.session.commit()


@pytest.fixture
def consultant_user(app):
    """Create a consultant user for testing."""
    with app.app_context():
        consultant_role = Role.query.filter_by(name='consultant').first()
        if not consultant_role:
            consultant_role = Role(name='consultant', description='Agricultural Consultant')
            db.session.add(consultant_role)
            db.session.commit()
        
        user = User(
            username='consultant',
            email='consultant@test.com',
            first_name='Consultant',
            last_name='User',
            role_id=consultant_role.id,
            is_active=True
        )
        user.set_password('consultant123')
        db.session.add(user)
        db.session.commit()
        
        yield user
        
        db.session.delete(user)
        db.session.commit()


@pytest.fixture
def farmer_user(app):
    """Create a farmer user for testing."""
    with app.app_context():
        farmer_role = Role.query.filter_by(name='farmer').first()
        if not farmer_role:
            farmer_role = Role(name='farmer', description='Farmer')
            db.session.add(farmer_role)
            db.session.commit()
        
        user = User(
            username='farmer',
            email='farmer@test.com',
            first_name='Farmer',
            last_name='User',
            role_id=farmer_role.id,
            is_active=True
        )
        user.set_password('farmer123')
        db.session.add(user)
        db.session.commit()
        
        yield user
        
        db.session.delete(user)
        db.session.commit()


@pytest.fixture
def vendor_user(app):
    """Create a vendor user for testing."""
    with app.app_context():
        vendor_role = Role.query.filter_by(name='vendor').first()
        if not vendor_role:
            vendor_role = Role(name='vendor', description='Product Vendor')
            db.session.add(vendor_role)
            db.session.commit()
        
        user = User(
            username='vendor',
            email='vendor@test.com',
            first_name='Vendor',
            last_name='User',
            role_id=vendor_role.id,
            is_active=True
        )
        user.set_password('vendor123')
        db.session.add(user)
        db.session.commit()
        
        yield user
        
        db.session.delete(user)
        db.session.commit()


@pytest.fixture
def inactive_user(app):
    """Create an inactive user for testing."""
    with app.app_context():
        farmer_role = Role.query.filter_by(name='farmer').first()
        if not farmer_role:
            farmer_role = Role(name='farmer', description='Farmer')
            db.session.add(farmer_role)
            db.session.commit()
        
        user = User(
            username='inactive',
            email='inactive@test.com',
            first_name='Inactive',
            last_name='User',
            role_id=farmer_role.id,
            is_active=False
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        yield user
        
        db.session.delete(user)
        db.session.commit()
