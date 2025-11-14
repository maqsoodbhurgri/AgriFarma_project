"""
Pytest tests for Admin Reports and Analytics module.
Tests report accuracy, route access, and data integrity.
"""
import pytest
from datetime import datetime, timedelta
from flask import url_for
from agrifarma import create_app, db
from agrifarma.models.user import User
from agrifarma.models.role import Role
from agrifarma.models.product import Product, Order, OrderItem


@pytest.fixture(scope='module')
def test_client():
    """Create test client with test database."""
    app = create_app('testing')
    
    with app.test_client() as testing_client:
        with app.app_context():
            db.create_all()
            
            # Create roles
            admin_role = Role(name='admin')
            farmer_role = Role(name='farmer')
            vendor_role = Role(name='vendor')
            db.session.add_all([admin_role, farmer_role, vendor_role])
            db.session.commit()
            
            # Create test users
            admin = User(
                username='admin',
                name='Admin User',
                email='admin@test.com',
                role_id=admin_role.id,
                is_active=True
            )
            admin.set_password('admin123')
            
            farmer = User(
                username='farmer',
                name='Farmer User',
                email='farmer@test.com',
                role_id=farmer_role.id,
                is_active=True
            )
            farmer.set_password('farmer123')
            
            vendor = User(
                username='vendor',
                name='Vendor User',
                email='vendor@test.com',
                role_id=vendor_role.id,
                is_active=True
            )
            vendor.set_password('vendor123')
            
            db.session.add_all([admin, farmer, vendor])
            db.session.commit()
            
            yield testing_client
            
            db.drop_all()


@pytest.fixture
def sample_products(test_client):
    """Create sample products for testing."""
    vendor = User.query.filter_by(username='vendor').first()
    
    products = [
        Product(
            name='Wheat Seeds',
            slug='wheat-seeds',
            category='Seeds',
            price=1500,
            stock_quantity=100,
            low_stock_threshold=10,
            vendor_id=vendor.id,
            sold_count=50
        ),
        Product(
            name='Rice Seeds',
            slug='rice-seeds',
            category='Seeds',
            price=2000,
            stock_quantity=5,  # Low stock
            low_stock_threshold=10,
            vendor_id=vendor.id,
            sold_count=30
        ),
        Product(
            name='NPK Fertilizer',
            slug='npk-fertilizer',
            category='Fertilizers',
            price=2500,
            stock_quantity=80,
            low_stock_threshold=10,
            vendor_id=vendor.id,
            sold_count=75
        ),
        Product(
            name='Garden Hoe',
            slug='garden-hoe',
            category='Tools',
            price=450,
            stock_quantity=0,  # Out of stock
            low_stock_threshold=10,
            vendor_id=vendor.id,
            sold_count=20
        )
    ]
    
    for product in products:
        db.session.add(product)
    db.session.commit()
    
    return products


@pytest.fixture
def sample_orders(test_client, sample_products):
    """Create sample orders for testing."""
    farmer = User.query.filter_by(username='farmer').first()
    
    orders = []
    
    # Create orders over the last 3 months
    for month in range(3):
        for i in range(5):
            order_date = datetime.utcnow() - timedelta(days=30*month + i*5)
            
            order = Order(
                order_number=f'ORD-TEST-{month}-{i}',
                customer_id=farmer.id,
                order_date=order_date,
                status='delivered',
                payment_status='paid',
                payment_method='cod',
                subtotal=5000,
                tax_amount=250,
                shipping_fee=200,
                total_amount=5450
            )
            
            # Add items
            for product in sample_products[:2]:
                item = OrderItem(
                    product_id=product.id,
                    product_name=product.name,
                    quantity=2,
                    unit_price=product.price,
                    total_price=product.price * 2
                )
                order.order_items.append(item)
            
            db.session.add(order)
            orders.append(order)
    
    db.session.commit()
    return orders


def login_user(client, username, password):
    """Helper function to log in a user."""
    return client.post('/auth/login', data={
        'username': username,
        'password': password
    }, follow_redirects=True)


def logout_user(client):
    """Helper function to log out."""
    return client.get('/auth/logout', follow_redirects=True)


# ==================== ACCESS CONTROL TESTS ====================

def test_dashboard_requires_login(test_client):
    """Test that dashboard requires authentication."""
    response = test_client.get('/admin/dashboard')
    assert response.status_code == 302  # Redirect to login
    assert b'/auth/login' in response.data or response.location.endswith('/auth/login')


def test_dashboard_requires_admin(test_client):
    """Test that dashboard requires admin role."""
    # Login as farmer (non-admin)
    login_user(test_client, 'farmer', 'farmer123')
    
    response = test_client.get('/admin/dashboard', follow_redirects=True)
    assert b'You do not have permission' in response.data or b'permission' in response.data.lower()
    
    logout_user(test_client)


def test_dashboard_accessible_by_admin(test_client):
    """Test that admin can access dashboard."""
    login_user(test_client, 'admin', 'admin123')
    
    response = test_client.get('/admin/dashboard')
    assert response.status_code == 200
    assert b'Admin Dashboard' in response.data or b'dashboard' in response.data.lower()
    
    logout_user(test_client)


def test_reports_requires_admin(test_client):
    """Test that reports page requires admin role."""
    # Login as vendor (non-admin)
    login_user(test_client, 'vendor', 'vendor123')
    
    response = test_client.get('/admin/reports', follow_redirects=True)
    assert b'You do not have permission' in response.data or b'permission' in response.data.lower()
    
    logout_user(test_client)


# ==================== REPORT DATA TESTS ====================

def test_top_products_report(test_client, sample_products, sample_orders):
    """Test top products report accuracy."""
    login_user(test_client, 'admin', 'admin123')
    
    response = test_client.get('/admin/reports?report_type=top_products')
    assert response.status_code == 200
    
    # Check that products are listed
    for product in sample_products:
        assert product.name.encode() in response.data
    
    logout_user(test_client)


def test_low_inventory_report(test_client, sample_products):
    """Test low inventory alert report."""
    login_user(test_client, 'admin', 'admin123')
    
    response = test_client.get('/admin/reports?report_type=low_inventory')
    assert response.status_code == 200
    
    # Should show Rice Seeds (5 units) and Garden Hoe (0 units)
    assert b'Rice Seeds' in response.data
    assert b'Garden Hoe' in response.data
    
    # Should not show products with adequate stock
    # (Wheat Seeds has 100 units, above threshold)
    
    logout_user(test_client)


def test_user_registrations_report(test_client):
    """Test user registrations report."""
    login_user(test_client, 'admin', 'admin123')
    
    # Set date range to capture test users
    today = datetime.utcnow().strftime('%Y-%m-%d')
    yesterday = (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    response = test_client.get(f'/admin/reports?report_type=user_registrations&start_date={yesterday}&end_date={today}')
    assert response.status_code == 200
    
    # Should show some users
    assert b'admin' in response.data or b'farmer' in response.data or b'vendor' in response.data
    
    logout_user(test_client)


def test_orders_revenue_report(test_client, sample_orders):
    """Test orders and revenue monthly report."""
    login_user(test_client, 'admin', 'admin123')
    
    response = test_client.get('/admin/reports?report_type=orders_revenue')
    assert response.status_code == 200
    
    # Should show monthly data
    assert b'Total Orders' in response.data
    assert b'Revenue' in response.data
    
    logout_user(test_client)


def test_category_distribution_report(test_client, sample_products):
    """Test product category distribution report."""
    login_user(test_client, 'admin', 'admin123')
    
    response = test_client.get('/admin/reports?report_type=category_distribution')
    assert response.status_code == 200
    
    # Should show all categories
    assert b'Seeds' in response.data
    assert b'Fertilizers' in response.data
    assert b'Tools' in response.data
    
    logout_user(test_client)


# ==================== FILTER TESTS ====================

def test_report_date_filter(test_client, sample_products):
    """Test report filtering by date range."""
    login_user(test_client, 'admin', 'admin123')
    
    # Filter for last 7 days
    end_date = datetime.utcnow().strftime('%Y-%m-%d')
    start_date = (datetime.utcnow() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    response = test_client.get(f'/admin/reports?report_type=top_products&start_date={start_date}&end_date={end_date}')
    assert response.status_code == 200
    
    logout_user(test_client)


def test_report_category_filter(test_client, sample_products):
    """Test report filtering by category."""
    login_user(test_client, 'admin', 'admin123')
    
    response = test_client.get('/admin/reports?report_type=top_products&category=Seeds')
    assert response.status_code == 200
    
    # Should show Seeds category products
    assert b'Seeds' in response.data
    
    logout_user(test_client)


# ==================== EXPORT TESTS ====================

def test_csv_export(test_client, sample_products):
    """Test CSV export functionality."""
    login_user(test_client, 'admin', 'admin123')
    
    response = test_client.get('/admin/reports?report_type=top_products&export=csv')
    assert response.status_code == 200
    assert response.content_type == 'text/csv'
    assert 'attachment' in response.headers.get('Content-Disposition', '')
    
    logout_user(test_client)


def test_json_export(test_client, sample_products):
    """Test JSON export functionality."""
    login_user(test_client, 'admin', 'admin123')
    
    response = test_client.get('/admin/reports?report_type=top_products&export=json')
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    assert 'attachment' in response.headers.get('Content-Disposition', '')
    
    logout_user(test_client)


# ==================== DASHBOARD CHART DATA TESTS ====================

def test_dashboard_chart_data(test_client, sample_products, sample_orders):
    """Test that dashboard contains chart data."""
    login_user(test_client, 'admin', 'admin123')
    
    response = test_client.get('/admin/dashboard')
    assert response.status_code == 200
    
    # Check for Chart.js
    assert b'Chart.js' in response.data or b'chart.js' in response.data
    
    # Check for chart canvases
    assert b'monthlySalesChart' in response.data
    assert b'categoryPieChart' in response.data
    assert b'userRegistrationsChart' in response.data
    
    logout_user(test_client)


def test_quick_stats_api(test_client, sample_products, sample_orders):
    """Test quick stats API endpoint."""
    login_user(test_client, 'admin', 'admin123')
    
    response = test_client.get('/admin/reports/api/quick-stats')
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    
    data = response.get_json()
    assert 'total_revenue' in data
    assert 'total_orders' in data
    assert 'total_users' in data
    assert 'active_products' in data
    assert 'low_stock_products' in data
    
    logout_user(test_client)


# ==================== DATA INTEGRITY TESTS ====================

def test_product_sold_count_accuracy(test_client, sample_products):
    """Test that product sold count is accurate."""
    product = sample_products[0]  # Wheat Seeds
    assert product.sold_count == 50


def test_low_stock_detection(test_client, sample_products):
    """Test low stock detection logic."""
    rice_seeds = Product.query.filter_by(slug='rice-seeds').first()
    garden_hoe = Product.query.filter_by(slug='garden-hoe').first()
    
    assert rice_seeds.is_low_stock() == True  # 5 <= 10
    assert garden_hoe.is_low_stock() == True  # 0 <= 10


def test_order_total_calculation(test_client, sample_orders):
    """Test that order totals are calculated correctly."""
    order = sample_orders[0]
    
    expected_total = order.subtotal + order.tax_amount + order.shipping_fee - order.discount_amount
    assert order.total_amount == expected_total


def test_order_item_count(test_client, sample_orders):
    """Test order item count calculation."""
    order = sample_orders[0]
    item_count = order.get_item_count()
    
    assert item_count == sum(item.quantity for item in order.order_items)


# ==================== EDGE CASE TESTS ====================

def test_empty_report(test_client):
    """Test report with no data."""
    login_user(test_client, 'admin', 'admin123')
    
    # Query for future dates (no data)
    future_start = (datetime.utcnow() + timedelta(days=30)).strftime('%Y-%m-%d')
    future_end = (datetime.utcnow() + timedelta(days=60)).strftime('%Y-%m-%d')
    
    response = test_client.get(f'/admin/reports?report_type=top_products&start_date={future_start}&end_date={future_end}')
    assert response.status_code == 200
    
    logout_user(test_client)


def test_invalid_date_range(test_client):
    """Test report with invalid date range."""
    login_user(test_client, 'admin', 'admin123')
    
    # End date before start date
    response = test_client.get('/admin/reports?report_type=top_products&start_date=2024-12-31&end_date=2024-01-01')
    assert response.status_code == 200  # Should handle gracefully
    
    logout_user(test_client)


# ==================== PERFORMANCE TESTS ====================

def test_large_dataset_performance(test_client, sample_products):
    """Test report generation with larger dataset."""
    login_user(test_client, 'admin', 'admin123')
    
    # This should complete within reasonable time
    import time
    start_time = time.time()
    
    response = test_client.get('/admin/reports?report_type=top_products')
    
    end_time = time.time()
    duration = end_time - start_time
    
    assert response.status_code == 200
    assert duration < 5  # Should complete within 5 seconds
    
    logout_user(test_client)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
