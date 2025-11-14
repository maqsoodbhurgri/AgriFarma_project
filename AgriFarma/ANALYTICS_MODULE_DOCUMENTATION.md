# Admin Reports and Analytics Module Documentation

## Overview
The Admin Reports and Analytics module provides comprehensive data insights, visual analytics, and export capabilities for AgriFarma administrators. Built with Flask, SQLAlchemy, Pandas, and Chart.js, this module enables data-driven decision-making through interactive dashboards and detailed reports.

---

## Features

### ✅ **Visual Analytics Dashboard**
- **Monthly Sales Chart** - Bar chart showing revenue and order count over 12 months
- **Category Distribution** - Pie chart displaying product distribution by category
- **User Registrations** - Line chart tracking new user sign-ups over time
- **Key Metrics Cards** - Summary statistics for revenue, users, products, and orders
- **Top Product Showcase** - Highlights best-selling product with detailed stats

### ✅ **Comprehensive Reports**
1. **Top Selling Products** - Best performers by units sold and revenue
2. **Low Inventory Alerts** - Products below stock threshold
3. **User Registrations** - New user sign-ups with details
4. **Orders & Revenue** - Monthly breakdown of sales performance
5. **Category Distribution** - Product analysis by category

### ✅ **Data Export**
- **CSV Export** - Download reports as comma-separated values
- **JSON Export** - Export data in JSON format for API integration
- **Pandas Integration** - Efficient data processing and aggregation

### ✅ **Security & Access Control**
- **Admin-Only Access** - Role-based authentication required
- **Login Protection** - All routes protected by `@login_required`
- **Permission Checks** - Custom `@admin_required` decorator

---

## Database Models

### Product Model
```python
Fields:
- name, slug, description, category, subcategory
- price, original_price, currency
- stock_quantity, low_stock_threshold, sku
- unit, weight, brand, manufacturer
- is_active, is_featured, in_stock
- vendor_id, view_count, sold_count, rating

Methods:
- is_low_stock() - Check if stock below threshold
- get_discount_percentage() - Calculate discount %
- update_stock(quantity_change) - Adjust inventory
- increment_views() - Track product views
- increment_sold(quantity) - Update sold count
```

### Order Model
```python
Fields:
- order_number, customer_id
- total_amount, subtotal, tax_amount, shipping_fee, discount_amount
- status (pending, processing, shipped, delivered, cancelled)
- payment_status, payment_method
- shipping details (name, address, city, state, phone)
- tracking_number, carrier
- order_date, paid_at, shipped_at, delivered_at

Methods:
- get_item_count() - Total items in order
- update_status(new_status) - Update status with timestamps
```

### OrderItem Model
```python
Fields:
- order_id, product_id
- product_name, product_sku
- quantity, unit_price, total_price
- discount_percent, discount_amount
```

---

## Routes

### Admin Dashboard
**Route:** `/admin/dashboard`  
**Methods:** GET  
**Access:** Admin only  
**Template:** `analytics/admin_dashboard.html`

**Functionality:**
- Displays 4 key metric cards (revenue, users, products, orders)
- Generates 3 interactive Chart.js visualizations
- Shows top-selling product details
- Provides quick action links to reports

**Data Processing:**
```python
# Monthly sales aggregation
monthly_sales = db.session.query(
    extract('year', Order.order_date).label('year'),
    extract('month', Order.order_date).label('month'),
    func.sum(Order.total_amount).label('revenue'),
    func.count(Order.id).label('order_count')
).filter(
    Order.order_date >= start_date,
    Order.status != 'cancelled'
).group_by('year', 'month').order_by('year', 'month').all()
```

### Admin Reports
**Route:** `/admin/reports`  
**Methods:** GET  
**Access:** Admin only  
**Template:** `analytics/admin_reports.html`

**Query Parameters:**
- `report_type` - Type of report (required)
- `start_date` - Filter start date (YYYY-MM-DD)
- `end_date` - Filter end date (YYYY-MM-DD)
- `category` - Filter by product category (optional)
- `export` - Export format ('csv' or 'json')

**Report Types:**
1. `top_products` - Top-selling products
2. `low_inventory` - Low stock alerts
3. `user_registrations` - New users
4. `orders_revenue` - Monthly orders/revenue
5. `category_distribution` - Category analysis

**Example Usage:**
```
/admin/reports?report_type=top_products&start_date=2024-01-01&end_date=2024-12-31&category=Seeds
```

### Quick Stats API
**Route:** `/admin/reports/api/quick-stats`  
**Methods:** GET  
**Access:** Admin only  
**Returns:** JSON

**Response Format:**
```json
{
  "total_revenue": 125000.00,
  "total_orders": 450,
  "total_users": 1250,
  "active_products": 85,
  "low_stock_products": 12,
  "recent_revenue": 15000.00,
  "recent_orders": 45,
  "new_users": 38
}
```

---

## Templates

### admin_dashboard.html

**Features:**
- 4 gradient metric cards (blue, green, yellow, red)
- 3 Chart.js visualizations:
  - **Bar Chart (Dual Axis):** Monthly revenue (left) and order count (right)
  - **Pie Chart:** Product category distribution with percentages
  - **Line Chart:** User registration trend with area fill
- Top product card with detailed stats
- Quick action links to all reports
- Responsive Bootstrap 5 grid layout

**Chart.js Configuration:**
```javascript
// Monthly Sales Bar Chart
const monthlySalesChart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: ['Jan 2024', 'Feb 2024', ...],
        datasets: [{
            label: 'Revenue (PKR)',
            data: [50000, 65000, ...],
            yAxisID: 'y'
        }, {
            label: 'Order Count',
            data: [120, 145, ...],
            yAxisID: 'y1'
        }]
    },
    options: {
        scales: {
            y: { position: 'left', title: 'Revenue (PKR)' },
            y1: { position: 'right', title: 'Order Count' }
        }
    }
});
```

### admin_reports.html

**Features:**
- Filter form with report type, date range, category
- Responsive data table with striped rows
- Export buttons (CSV, JSON) in card header
- Report summary alert showing record count
- Collapsible accordion with report descriptions
- Auto-submit on date/category change

**Data Table:**
```html
<table class="table table-striped table-hover" id="reportTable">
    <thead class="thead-dark">
        <tr>
            {% for column in columns %}
            <th>{{ column }}</th>
            {% endfor %}
        </tr>
    </thead>
    <tbody>
        {% for row in report_data %}
        <tr>
            {% for column in columns %}
            <td>{{ row[column] }}</td>
            {% endfor %}
        </tr>
        {% endfor %}
    </tbody>
</table>
```

---

## Usage Guide

### For Administrators:

#### Viewing Analytics Dashboard:
1. Login with admin credentials
2. Navigate to **Analytics Dashboard** from sidebar
3. View key metrics in colored cards
4. Analyze charts for trends and insights
5. Click on top product for more details
6. Use quick action links to access specific reports

#### Generating Reports:
1. Navigate to **Reports & Export**
2. Select report type from dropdown
3. Set date range (optional, defaults to last 30 days)
4. Filter by category if needed
5. Click "Generate Report"
6. Review data in table format
7. Export as CSV or JSON if needed

#### Exporting Data:
1. Generate desired report
2. Click "Export CSV" or "Export JSON" button
3. File downloads automatically with timestamp
4. Open in Excel (CSV) or use in API (JSON)

---

## Installation & Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

**New dependencies:**
- `pandas==2.1.4` - Data analysis and manipulation
- `numpy==1.26.2` - Numerical computing (pandas dependency)

### 2. Database Migration
```bash
# Create migration for new models
flask db migrate -m "Add Product, Order, OrderItem models for analytics"

# Apply migration
flask db upgrade
```

### 3. Seed Sample Data (Optional)
```bash
# Generate sample products and orders for testing
flask seed_data
```

This creates:
- Sample products across 5 categories (Seeds, Fertilizers, Pesticides, Tools, Equipment)
- Sample orders over last 12 months
- Test vendor and customer users

### 4. Verify Installation
```bash
# Start Flask development server
flask run

# Visit dashboard
http://localhost:5000/admin/dashboard

# Visit reports
http://localhost:5000/admin/reports
```

---

## Testing

### Running Tests
```bash
# Run all analytics tests
pytest tests/test_analytics.py -v

# Run with coverage
pytest tests/test_analytics.py --cov=agrifarma.routes.analytics --cov-report=html

# Run specific test
pytest tests/test_analytics.py::test_dashboard_accessible_by_admin -v
```

### Test Coverage

**Access Control Tests (6 tests):**
- ✅ Dashboard requires login
- ✅ Dashboard requires admin role
- ✅ Reports requires admin role
- ✅ Non-admins denied access
- ✅ Admin can access dashboard
- ✅ Admin can access reports

**Report Data Tests (5 tests):**
- ✅ Top products report accuracy
- ✅ Low inventory detection
- ✅ User registrations report
- ✅ Orders & revenue monthly breakdown
- ✅ Category distribution analysis

**Filter Tests (2 tests):**
- ✅ Date range filtering
- ✅ Category filtering

**Export Tests (2 tests):**
- ✅ CSV export with correct headers
- ✅ JSON export with valid format

**Chart Data Tests (2 tests):**
- ✅ Dashboard contains Chart.js
- ✅ Quick stats API returns JSON

**Data Integrity Tests (4 tests):**
- ✅ Product sold count accuracy
- ✅ Low stock detection logic
- ✅ Order total calculation
- ✅ Order item count

**Edge Case Tests (2 tests):**
- ✅ Empty report handling
- ✅ Invalid date range handling

**Performance Tests (1 test):**
- ✅ Large dataset performance (<5s)

### Test Sample Output
```
tests/test_analytics.py::test_dashboard_requires_login PASSED
tests/test_analytics.py::test_dashboard_requires_admin PASSED
tests/test_analytics.py::test_dashboard_accessible_by_admin PASSED
tests/test_analytics.py::test_top_products_report PASSED
tests/test_analytics.py::test_low_inventory_report PASSED
tests/test_analytics.py::test_csv_export PASSED
tests/test_analytics.py::test_json_export PASSED
tests/test_analytics.py::test_quick_stats_api PASSED

======================== 24 passed in 3.45s ========================
```

---

## API Reference

### Export Report Function
```python
def export_report(data, columns, report_name, export_format):
    """
    Export report data as CSV or JSON.
    
    Args:
        data: List of dictionaries containing report data
        columns: List of column names
        report_name: Name of the report
        export_format: 'csv' or 'json'
    
    Returns:
        Flask response with appropriate content type
    """
```

**Usage:**
```python
report_data = [
    {'Product': 'Wheat Seeds', 'Sales': 50, 'Revenue': 75000},
    {'Product': 'Rice Seeds', 'Sales': 30, 'Revenue': 60000}
]
columns = ['Product', 'Sales', 'Revenue']

response = export_report(report_data, columns, 'top_products', 'csv')
```

---

## Configuration

### Pagination Settings
Edit in `agrifarma/routes/analytics.py`:
```python
# Line 198: Top products limit
products = query.order_by(Product.sold_count.desc()).limit(100).all()

# Adjust to show more/fewer products
products = query.order_by(Product.sold_count.desc()).limit(200).all()
```

### Date Range Defaults
```python
# Line 53: Dashboard date range (last 12 months)
start_date = end_date - timedelta(days=365)

# Line 169: Reports default (last 30 days)
start_date = datetime.utcnow() - timedelta(days=30)
```

### Chart Colors
Edit in `admin_dashboard.html`:
```javascript
const chartColors = {
    primary: 'rgba(4, 169, 245, 0.8)',
    success: 'rgba(40, 199, 111, 0.8)',
    warning: 'rgba(255, 193, 7, 0.8)',
    danger: 'rgba(242, 17, 54, 0.8)',
    info: 'rgba(69, 170, 242, 0.8)',
    purple: 'rgba(140, 82, 255, 0.8)'
};
```

---

## Troubleshooting

### Issue: Charts not displaying
**Check:**
- Chart.js CDN loaded correctly
- Data passed as JSON: `{{ sales_labels|safe }}`
- Canvas elements exist with correct IDs
- JavaScript console for errors

### Issue: Reports showing no data
**Check:**
- Database contains products/orders
- Date range includes existing data
- Filters not too restrictive
- `is_deleted=False` conditions applied

### Issue: Export not working
**Check:**
- pandas installed: `pip install pandas`
- Report generated before export
- Browser allows file downloads
- No popup blockers active

### Issue: Permission denied
**Check:**
- User logged in with admin account
- User role is 'admin' (not 'farmer', 'vendor', etc.)
- `current_user.role.name == 'admin'`
- Session not expired

---

## Performance Optimization

### Database Indexing
```python
# Already implemented in models
Product.name - index=True
Product.slug - unique=True, index=True
Product.category - index=True
Order.order_number - unique=True, index=True
User.username - unique=True, index=True
User.email - unique=True, index=True
```

### Query Optimization
```python
# Use aggregation instead of loading all records
total_revenue = db.session.query(
    func.sum(Order.total_amount)
).filter(Order.status != 'cancelled').scalar()

# Instead of:
# orders = Order.query.filter_by(status='delivered').all()
# total_revenue = sum(order.total_amount for order in orders)
```

### Caching Recommendations
```python
# For production, add caching to expensive queries
from flask_caching import Cache

cache = Cache(config={'CACHE_TYPE': 'simple'})

@cache.cached(timeout=300, key_prefix='dashboard_stats')
def get_dashboard_stats():
    # Expensive calculations here
    return stats
```

---

## Security Considerations

### Implemented:
✅ Admin-only access control with decorator
✅ Login required for all routes
✅ CSRF protection on forms (Flask-WTF)
✅ SQL injection prevention (SQLAlchemy ORM)
✅ XSS prevention (Jinja2 auto-escaping)
✅ Role-based permissions

### Recommended for Production:
⚠️ Rate limiting on API endpoints
⚠️ HTTPS enforcement
⚠️ Audit logging for data exports
⚠️ Data anonymization in reports
⚠️ IP whitelisting for admin access

---

## Future Enhancements

### Potential Features:
1. **Real-time Updates** - WebSocket integration for live data
2. **Custom Date Ranges** - Advanced date picker with presets
3. **Email Reports** - Schedule automated report delivery
4. **Predictive Analytics** - ML-based sales forecasting
5. **More Chart Types** - Donut, scatter, heatmap charts
6. **PDF Export** - Generate printable PDF reports
7. **Dashboard Customization** - User-defined widgets
8. **Comparative Analysis** - Year-over-year comparisons
9. **Geolocation Analytics** - Sales by region/city
10. **Inventory Forecasting** - Predict restock needs

---

## File Structure

```
agrifarma/
├── models/
│   └── product.py              # Product, Order, OrderItem models
├── routes/
│   └── analytics.py            # Dashboard and reports routes
└── templates/
    └── analytics/
        ├── admin_dashboard.html # Visual analytics with charts
        └── admin_reports.html   # Tabular reports with export

tests/
└── test_analytics.py           # Comprehensive test suite (24 tests)

app.py                           # CLI command: flask seed_data
requirements.txt                 # Added pandas==2.1.4, numpy==1.26.2
```

---

## CLI Commands

### Initialize Database
```bash
flask init_db
```

### Create Admin User
```bash
flask create_admin
# Enter email, username, password interactively
```

### Seed Sample Data
```bash
flask seed_data
# Creates sample products, orders, and users
```

### Database Migrations
```bash
# Create migration
flask db migrate -m "Description"

# Apply migration
flask db upgrade

# Rollback migration
flask db downgrade
```

---

## Version Info

- **Module Version:** 1.0.0
- **Created:** November 2025
- **Framework:** Flask 3.0.0
- **Database:** SQLAlchemy 2.0.23
- **Analytics:** Pandas 2.1.4
- **Visualization:** Chart.js 3.9.1
- **Theme:** Datta Able Admin Template

---

## Support

For issues or questions:
1. Check this documentation
2. Review test cases in `tests/test_analytics.py`
3. Examine route implementations in `agrifarma/routes/analytics.py`
4. Inspect template files for UI customization

---

**Built with ❤️ for AgriFarma - Empowering Sindh Farmers with Data-Driven Insights**
