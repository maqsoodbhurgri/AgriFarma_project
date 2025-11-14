"""
Seed script to add dummy products to marketplace.
Run this after setting up the database.
"""
import sys
from app import app
from agrifarma.extensions import db
from agrifarma.models.user import User
from agrifarma.models.product import Product
from datetime import datetime


def seed_products():
    """Add dummy products with realistic agricultural items."""
    
    with app.app_context():
        # Find a vendor user (or use first user)
        vendor = User.query.filter_by(role_id=3).first()  # farmer/vendor role
        if not vendor:
            vendor = User.query.first()
        
        if not vendor:
            print("❌ No users found. Please create a user first.")
            return
        
        print(f"✅ Using vendor: {vendor.username}")
        
        # Delete existing products to avoid duplicates
        Product.query.delete()
        db.session.commit()
        print("🗑️  Cleared existing products")
        
        # Define dummy products with realistic Pakistani agricultural items
        products = [
            {
                'name': 'Premium Wheat Seeds (خالص گندم کے بیج)',
                'slug': 'premium-wheat-seeds',
                'description': 'High-quality certified wheat seeds suitable for Sindh climate. Disease resistant with excellent yield potential. Perfect for both irrigated and rain-fed areas.',
                'category': 'Seeds',
                'subcategory': 'Cereal Seeds',
                'price': 5500.0,
                'original_price': 6500.0,
                'stock_quantity': 150,
                'unit': '50kg bag',
                'weight': 50.0,
                'brand': 'AgriPak Seeds',
                'manufacturer': 'Punjab Seed Corporation',
                'image_url': 'images/products/wheat-seeds.jpg',
                'is_featured': True,
                'vendor_id': vendor.id,
                'sku': 'WS-2024-001',
                'rating': 4.5,
                'review_count': 23,
                'meta_title': 'Buy Premium Wheat Seeds Online in Pakistan',
                'meta_description': 'Certified wheat seeds for high yield farming in Sindh'
            },
            {
                'name': 'Basmati Rice Seeds (بासمتی چاول کے بیج)',
                'slug': 'basmati-rice-seeds',
                'description': 'Certified Basmati rice seeds with superior grain quality and aroma. Ideal for Sindh irrigation system with 120-day maturity period.',
                'category': 'Seeds',
                'subcategory': 'Rice Seeds',
                'price': 8500.0,
                'original_price': 9500.0,
                'stock_quantity': 80,
                'unit': '25kg bag',
                'weight': 25.0,
                'brand': 'Golden Rice',
                'manufacturer': 'Sindh Seed Company',
                'image_url': 'images/products/rice-seeds.jpg',
                'is_featured': True,
                'vendor_id': vendor.id,
                'sku': 'RS-2024-002',
                'rating': 4.8,
                'review_count': 45,
                'meta_title': 'Basmati Rice Seeds for Sale',
                'meta_description': 'Premium basmati rice seeds for Pakistani farmers'
            },
            {
                'name': 'Hybrid Corn Seeds (مکئی کے ہائبرڈ بیج)',
                'slug': 'hybrid-corn-seeds',
                'description': 'High-yielding hybrid corn seeds resistant to local pests. Suitable for both kharif and rabi seasons with excellent germination rate.',
                'category': 'Seeds',
                'subcategory': 'Cereal Seeds',
                'price': 4200.0,
                'stock_quantity': 200,
                'unit': '20kg bag',
                'weight': 20.0,
                'brand': 'FMC Seeds',
                'manufacturer': 'Four Brothers Seed',
                'image_url': 'images/products/corn-seeds.jpg',
                'is_featured': True,
                'vendor_id': vendor.id,
                'sku': 'CS-2024-003',
                'rating': 4.3,
                'review_count': 18,
                'meta_title': 'Buy Hybrid Corn Seeds Online',
                'meta_description': 'Best corn seeds for Pakistani agriculture'
            },
            {
                'name': 'NPK Fertilizer (این پی کے کھاد)',
                'slug': 'npk-fertilizer',
                'description': 'Balanced NPK fertilizer (15-15-15) for all crops. Improves soil fertility and crop yield. Water-soluble and quick-acting formula.',
                'category': 'Fertilizers',
                'subcategory': 'Chemical Fertilizers',
                'price': 3800.0,
                'original_price': 4200.0,
                'stock_quantity': 300,
                'unit': '50kg bag',
                'weight': 50.0,
                'brand': 'Engro Fertilizers',
                'manufacturer': 'Engro Corporation',
                'image_url': 'images/products/fertilizer.jpg',
                'is_featured': True,
                'vendor_id': vendor.id,
                'sku': 'NPK-2024-004',
                'rating': 4.6,
                'review_count': 67,
                'meta_title': 'NPK Fertilizer for Agriculture',
                'meta_description': 'Quality NPK fertilizer for better crop growth'
            },
            {
                'name': 'Organic Compost (نامیاتی کھاد)',
                'slug': 'organic-compost',
                'description': 'Premium organic compost made from natural materials. Enriches soil, improves water retention, and promotes healthy plant growth naturally.',
                'category': 'Fertilizers',
                'subcategory': 'Organic Fertilizers',
                'price': 2500.0,
                'stock_quantity': 120,
                'unit': '40kg bag',
                'weight': 40.0,
                'brand': 'Green Earth',
                'manufacturer': 'Organic Farms Pakistan',
                'image_url': 'images/products/organic-fertilizer.jpg',
                'vendor_id': vendor.id,
                'sku': 'OC-2024-005',
                'rating': 4.7,
                'review_count': 34,
                'meta_title': 'Buy Organic Compost Online',
                'meta_description': 'Natural organic compost for sustainable farming'
            },
            {
                'name': 'Mini Tractor 40HP (چھوٹا ٹریکٹر)',
                'slug': 'mini-tractor-40hp',
                'description': '40 HP compact tractor perfect for small to medium farms. Fuel-efficient with excellent maneuverability. Includes warranty and maintenance support.',
                'category': 'Machinery',
                'subcategory': 'Tractors',
                'price': 850000.0,
                'original_price': 950000.0,
                'stock_quantity': 5,
                'unit': 'piece',
                'brand': 'Millat Tractors',
                'manufacturer': 'Millat Equipment Limited',
                'image_url': 'images/products/tractor.jpg',
                'is_featured': True,
                'vendor_id': vendor.id,
                'sku': 'TR-2024-006',
                'rating': 4.9,
                'review_count': 12,
                'meta_title': '40HP Tractor for Sale in Pakistan',
                'meta_description': 'Compact mini tractor for small farms'
            },
            {
                'name': 'Water Pump 3HP (پانی کا پمپ)',
                'slug': 'water-pump-3hp',
                'description': 'High-performance 3HP water pump for irrigation. Low electricity consumption with high water output. Suitable for 5-10 acre farms.',
                'category': 'Machinery',
                'subcategory': 'Irrigation Equipment',
                'price': 45000.0,
                'stock_quantity': 25,
                'unit': 'piece',
                'brand': 'Honda Pakistan',
                'manufacturer': 'Atlas Honda',
                'image_url': 'images/products/irrigation-pump.jpg',
                'vendor_id': vendor.id,
                'sku': 'WP-2024-007',
                'rating': 4.4,
                'review_count': 28,
                'meta_title': '3HP Water Pump for Agriculture',
                'meta_description': 'Reliable water pump for farm irrigation'
            },
            {
                'name': 'Pesticide Sprayer (کیڑے مار سپرے)',
                'slug': 'pesticide-sprayer',
                'description': 'Manual pesticide sprayer with 16-liter capacity. Adjustable nozzle for different spray patterns. Ergonomic design for comfortable use.',
                'category': 'Tools',
                'subcategory': 'Spray Equipment',
                'price': 6500.0,
                'original_price': 7500.0,
                'stock_quantity': 50,
                'unit': 'piece',
                'brand': 'AgriTech',
                'manufacturer': 'Pakistan Agricultural Tools',
                'image_url': 'images/products/pesticide-spray.jpg',
                'vendor_id': vendor.id,
                'sku': 'PS-2024-008',
                'rating': 4.2,
                'review_count': 15,
                'meta_title': 'Buy Pesticide Sprayer Online',
                'meta_description': 'Manual sprayer for crop protection'
            },
            {
                'name': 'Garden Tool Set (باغبانی کے اوزار)',
                'slug': 'garden-tool-set',
                'description': 'Complete 5-piece garden tool set including spade, fork, hoe, rake, and trowel. Made from high-quality steel with wooden handles.',
                'category': 'Tools',
                'subcategory': 'Hand Tools',
                'price': 3500.0,
                'stock_quantity': 75,
                'unit': 'set',
                'brand': 'Farm Master',
                'manufacturer': 'Sialkot Tools Industry',
                'image_url': 'images/products/hand-tools.jpg',
                'vendor_id': vendor.id,
                'sku': 'GT-2024-009',
                'rating': 4.5,
                'review_count': 22,
                'meta_title': 'Garden Tool Set for Farmers',
                'meta_description': 'Professional garden tools for farming'
            },
            {
                'name': 'Drip Irrigation Kit (ڈرپ آبپاشی کٹ)',
                'slug': 'drip-irrigation-kit',
                'description': 'Complete drip irrigation system for 1 acre. Saves 70% water compared to flood irrigation. Includes pipes, emitters, and fittings.',
                'category': 'Machinery',
                'subcategory': 'Irrigation Equipment',
                'price': 35000.0,
                'original_price': 40000.0,
                'stock_quantity': 15,
                'unit': '1 acre kit',
                'brand': 'Netafim Pakistan',
                'manufacturer': 'Drip Tech Pakistan',
                'image_url': 'images/products/drip-irrigation.jpg',
                'is_featured': True,
                'vendor_id': vendor.id,
                'sku': 'DI-2024-010',
                'rating': 4.8,
                'review_count': 31,
                'meta_title': 'Drip Irrigation System for Sale',
                'meta_description': 'Water-saving drip irrigation for modern farming'
            }
        ]
        
        # Add products to database
        added = 0
        for prod_data in products:
            product = Product(**prod_data)
            db.session.add(product)
            added += 1
            print(f"✅ Added: {product.name}")
        
        db.session.commit()
        print(f"\n🎉 Successfully added {added} products to marketplace!")
        print(f"📊 Featured products: {sum(1 for p in products if p.get('is_featured', False))}")
        print("\n💡 Tip: Visit /marketplace to see the products")


if __name__ == '__main__':
    try:
        seed_products()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
