"""
Test script to verify profile pages work correctly
"""
from agrifarma import create_app
from agrifarma.extensions import db
from agrifarma.models.user import User

app = create_app('development')

with app.test_client() as client:
    with app.app_context():
        # Get a test user
        user = User.query.filter_by(username='aijaz12').first()
        if not user:
            user = User.query.first()
        
        print(f"Testing with user: {user.username} ({user.email})")
        
        # Test 1: Access profile without login (should redirect to login)
        print("\n1. Testing /auth/profile without login...")
        response = client.get('/auth/profile')
        print(f"   Status: {response.status_code}")
        print(f"   Redirected to: {response.location if response.status_code == 302 else 'N/A'}")
        
        # Test 2: Login
        print("\n2. Testing login...")
        response = client.post('/auth/login', data={
            'username': user.username,
            'password': 'password123',  # Default password
            'remember_me': False
        }, follow_redirects=False)
        print(f"   Status: {response.status_code}")
        
        # Test 3: Access profile after login
        print("\n3. Testing /auth/profile after login...")
        response = client.get('/auth/profile', follow_redirects=True)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            # Check if our new template content is there
            data = response.data.decode('utf-8')
            if 'profile-hero' in data:
                print("   ✓ New modern profile template loaded!")
            elif 'Profile Information' in data:
                print("   ✓ Profile page loaded (but might be old template)")
            else:
                print("   ✗ Profile page loaded but content unclear")
            
            # Check for stats
            if 'Blog Posts' in data and 'stat-gradient' in data:
                print("   ✓ Stats cards present")
        else:
            print(f"   ✗ Failed to load profile: {response.status_code}")
        
        # Test 4: Access edit profile
        print("\n4. Testing /auth/edit-profile...")
        response = client.get('/auth/edit-profile')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.data.decode('utf-8')
            if 'avatar-edit' in data:
                print("   ✓ New edit profile template loaded!")
            elif 'Edit Profile' in data:
                print("   ✓ Edit profile page loaded")
        
        print("\n✅ All tests completed!")
