"""
Test all major pages to ensure they load without errors
"""
from agrifarma import create_app
from agrifarma.extensions import db
from agrifarma.models.user import User

app = create_app('development')

# Test routes (without auth required)
public_routes = [
    ('/', 'Home'),
    ('/auth/login', 'Login'),
    ('/auth/register', 'Register'),
    ('/blog/', 'Blog'),
    ('/forum/', 'Forum'),
    ('/marketplace/', 'Marketplace'),
    ('/consultancy/', 'Consultants'),
]

# Test routes (auth required)
protected_routes = [
    ('/dashboard', 'Dashboard'),
    ('/auth/profile', 'Profile'),
    ('/auth/edit-profile', 'Edit Profile'),
]

print("=" * 60)
print("TESTING PUBLIC PAGES (No Login Required)")
print("=" * 60)

with app.test_client() as client:
    for route, name in public_routes:
        try:
            response = client.get(route, follow_redirects=False)
            status = response.status_code
            
            if status == 200:
                print(f"OK  {status} - {name:20} ({route})")
            elif status == 302:
                print(f"=>  {status} - {name:20} ({route}) -> {response.location}")
            elif status == 404:
                print(f"ERR {status} - {name:20} ({route}) NOT FOUND")
            else:
                print(f"!!! {status} - {name:20} ({route})")
        except Exception as e:
            print(f"FAIL    - {name:20} ({route}) - {str(e)[:40]}")

print("\n" + "=" * 60)
print("TESTING PROTECTED PAGES (Login Required)")
print("=" * 60)

with app.test_client() as client:
    with app.app_context():
        # Get a test user
        user = User.query.filter_by(username='farmer1').first()
        if not user:
            user = User.query.first()
        
        if user:
            # Login by setting session manually (simpler than CSRF handling)
            with client.session_transaction() as sess:
                sess['_user_id'] = str(user.id)
                sess['_fresh'] = True
            
            for route, name in protected_routes:
                try:
                    response = client.get(route, follow_redirects=False)
                    status = response.status_code
                    
                    if status == 200:
                        # Check if our new templates are being used
                        html = response.data.decode('utf-8')
                        
                        # Profile page checks
                        if 'profile' in route.lower():
                            if 'profile-hero' in html or 'stat-gradient' in html:
                                print(f"OK  {status} - {name:20} ({route}) [NEW DESIGN]")
                            elif 'Profile Information' in html:
                                print(f"OK  {status} - {name:20} ({route}) [OLD DESIGN]")
                            else:
                                print(f"OK  {status} - {name:20} ({route})")
                        else:
                            print(f"OK  {status} - {name:20} ({route})")
                    elif status == 302:
                        print(f"=>  {status} - {name:20} ({route}) -> {response.location}")
                    elif status == 404:
                        print(f"ERR {status} - {name:20} ({route}) NOT FOUND")
                    else:
                        print(f"!!! {status} - {name:20} ({route})")
                except Exception as e:
                    print(f"FAIL    - {name:20} ({route}) - {str(e)[:40]}")
        else:
            print("No users found in database!")

print("\n" + "=" * 60)
print("TESTING COMPLETE")
print("=" * 60)
print("\nLegend:")
print("  OK  - Page loaded successfully")
print("  =>  - Redirect (expected for some pages)")
print("  ERR - Page not found (404)")
print("  !!! - Other error")
print("  FAIL - Exception occurred")
