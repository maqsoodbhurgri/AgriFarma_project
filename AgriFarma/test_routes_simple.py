"""Simple route testing script - tests if routes are accessible."""

import sys
from flask import Flask
from agrifarma import create_app

def test_routes():
    """Test if main routes are accessible."""
    app = create_app()
    
    with app.test_client() as client:
        print("\n=== Testing Routes ===\n")
        
        # Test routes that don't require login
        routes_to_test = [
            ('/auth/login', 'Login Page'),
            ('/auth/register', 'Register Page'),
            ('/forum', 'Forum'),
            ('/marketplace', 'Marketplace'),
            ('/consultancy/consultants', 'Consultants'),
            ('/blog', 'Blogs'),
        ]
        
        for route, name in routes_to_test:
            try:
                response = client.get(route, follow_redirects=True)
                status = "✓ OK" if response.status_code == 200 else f"✗ ERROR ({response.status_code})"
                print(f"{status} - {name} ({route})")
                
                if response.status_code != 200:
                    print(f"   Response: {response.data[:200]}")
                    
            except Exception as e:
                print(f"✗ FAILED - {name} ({route})")
                print(f"   Error: {str(e)}")
        
        print("\n=== Test Complete ===\n")

if __name__ == '__main__':
    test_routes()
