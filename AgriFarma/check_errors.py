"""Check for all errors in the AgriFarma application"""
import sys
import traceback

def check_imports():
    """Test all critical imports"""
    print("=" * 60)
    print("1. CHECKING IMPORTS")
    print("=" * 60)
    
    checks = [
        ("Flask", "flask"),
        ("SQLAlchemy", "flask_sqlalchemy"),
        ("Flask-Login", "flask_login"),
        ("Flask-WTF", "flask_wtf"),
        ("App creation", "agrifarma"),
        ("Extensions", "agrifarma.extensions"),
        ("Models", "agrifarma.models.user"),
    ]
    
    passed = 0
    failed = 0
    
    for name, module in checks:
        try:
            __import__(module)
            print(f"✓ {name}: OK")
            passed += 1
        except Exception as e:
            print(f"✗ {name}: FAILED - {str(e)}")
            failed += 1
            
    print(f"\nImport Results: {passed} passed, {failed} failed\n")
    return failed == 0

def check_app_creation():
    """Test app creation"""
    print("=" * 60)
    print("2. CHECKING APP CREATION")
    print("=" * 60)
    
    try:
        from agrifarma import create_app
        app = create_app()
        print(f"✓ App created successfully")
        print(f"✓ App name: {app.name}")
        print(f"✓ Debug mode: {app.debug}")
        print(f"✓ Testing mode: {app.testing}")
        return True, app
    except Exception as e:
        print(f"✗ App creation failed: {str(e)}")
        traceback.print_exc()
        return False, None

def check_blueprints(app):
    """Check registered blueprints"""
    print("\n" + "=" * 60)
    print("3. CHECKING BLUEPRINTS")
    print("=" * 60)
    
    try:
        blueprints = [bp.name for bp in app.blueprints.values()]
        print(f"✓ Total blueprints: {len(blueprints)}")
        for bp in blueprints:
            print(f"  - {bp}")
        return True
    except Exception as e:
        print(f"✗ Blueprint check failed: {str(e)}")
        return False

def check_routes(app):
    """Check registered routes"""
    print("\n" + "=" * 60)
    print("4. CHECKING ROUTES")
    print("=" * 60)
    
    try:
        routes = []
        for rule in app.url_map.iter_rules():
            if rule.endpoint != 'static':
                routes.append(f"{rule.endpoint}: {rule.rule} {list(rule.methods - {'HEAD', 'OPTIONS'})}")
        
        print(f"✓ Total routes: {len(routes)}")
        
        # Group by prefix
        auth_routes = [r for r in routes if '/auth/' in r]
        forum_routes = [r for r in routes if '/forum/' in r]
        blog_routes = [r for r in routes if '/blog/' in r]
        marketplace_routes = [r for r in routes if '/marketplace/' in r]
        consultancy_routes = [r for r in routes if '/consultancy/' in r]
        admin_routes = [r for r in routes if '/admin/' in r]
        
        print(f"  - Auth routes: {len(auth_routes)}")
        print(f"  - Forum routes: {len(forum_routes)}")
        print(f"  - Blog routes: {len(blog_routes)}")
        print(f"  - Marketplace routes: {len(marketplace_routes)}")
        print(f"  - Consultancy routes: {len(consultancy_routes)}")
        print(f"  - Admin routes: {len(admin_routes)}")
        
        return True
    except Exception as e:
        print(f"✗ Route check failed: {str(e)}")
        return False

def check_database(app):
    """Check database connection"""
    print("\n" + "=" * 60)
    print("5. CHECKING DATABASE")
    print("=" * 60)
    
    try:
        from agrifarma.extensions import db
        from agrifarma.models.role import Role
        
        with app.app_context():
            # Check if database exists
            roles = Role.query.all()
            print(f"✓ Database connected")
            print(f"✓ Roles in database: {len(roles)}")
            for role in roles:
                print(f"  - {role.name}")
            return True
    except Exception as e:
        print(f"✗ Database check failed: {str(e)}")
        traceback.print_exc()
        return False

def check_templates(app):
    """Check template configuration"""
    print("\n" + "=" * 60)
    print("6. CHECKING TEMPLATE CONFIGURATION")
    print("=" * 60)
    
    try:
        import os
        template_folder = app.template_folder
        static_folder = app.static_folder
        
        print(f"✓ Template folder: {template_folder}")
        print(f"  Exists: {os.path.exists(template_folder)}")
        
        print(f"✓ Static folder: {static_folder}")
        print(f"  Exists: {os.path.exists(static_folder)}")
        
        # Check key templates
        key_templates = [
            'home/index.html',
            'accounts/login.html',
            'accounts/register.html',
            'blog/index.html',
            'consultancy/index.html',
        ]
        
        print("\n  Key templates:")
        for tmpl in key_templates:
            path = os.path.join(template_folder, tmpl)
            exists = os.path.exists(path)
            status = "✓" if exists else "✗"
            print(f"  {status} {tmpl}")
        
        return True
    except Exception as e:
        print(f"✗ Template check failed: {str(e)}")
        return False

def check_static_files(app):
    """Check static files"""
    print("\n" + "=" * 60)
    print("7. CHECKING STATIC FILES")
    print("=" * 60)
    
    try:
        import os
        static_folder = app.static_folder
        
        key_static = [
            'css/style.css',
            'css/dark.css',
            'js/pcoded.min.js',
            'js/vendor-all.min.js',
        ]
        
        print("  Key static files:")
        for static_file in key_static:
            path = os.path.join(static_folder, static_file)
            exists = os.path.exists(path)
            status = "✓" if exists else "✗"
            print(f"  {status} {static_file}")
        
        return True
    except Exception as e:
        print(f"✗ Static file check failed: {str(e)}")
        return False

def main():
    """Run all checks"""
    print("\n" + "=" * 60)
    print("AGRIFARMA ERROR CHECK")
    print("=" * 60 + "\n")
    
    print(f"Python version: {sys.version}\n")
    
    # Run checks
    checks_passed = []
    
    # 1. Imports
    checks_passed.append(check_imports())
    
    # 2. App creation
    app_ok, app = check_app_creation()
    checks_passed.append(app_ok)
    
    if app:
        # 3. Blueprints
        checks_passed.append(check_blueprints(app))
        
        # 4. Routes
        checks_passed.append(check_routes(app))
        
        # 5. Database
        checks_passed.append(check_database(app))
        
        # 6. Templates
        checks_passed.append(check_templates(app))
        
        # 7. Static files
        checks_passed.append(check_static_files(app))
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    total_checks = len(checks_passed)
    passed = sum(checks_passed)
    failed = total_checks - passed
    
    print(f"Total checks: {total_checks}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n✓✓✓ ALL CHECKS PASSED ✓✓✓")
    else:
        print(f"\n✗✗✗ {failed} CHECK(S) FAILED ✗✗✗")
    
    return failed == 0

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
