"""
Deployment preparation script for AgriFarma.
Run this before deploying to verify everything is ready.
"""
import os
import sys
import subprocess
from pathlib import Path


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_success(text):
    """Print success message."""
    print(f"✅ {text}")


def print_error(text):
    """Print error message."""
    print(f"❌ {text}")


def print_warning(text):
    """Print warning message."""
    print(f"⚠️  {text}")


def check_python_version():
    """Check if Python version is 3.8 or higher."""
    print_header("Checking Python Version")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print_success(f"Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print_error(f"Python {version.major}.{version.minor} (3.8+ required)")
        return False


def check_files_exist():
    """Check if required files exist."""
    print_header("Checking Required Files")
    
    required_files = [
        'requirements.txt',
        'config.py',
        'app.py',
        'wsgi.py',
        'Procfile',
        'README.md',
        '.gitignore',
        '.env.example'
    ]
    
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print_success(f"{file}")
        else:
            print_error(f"{file} - Missing!")
            all_exist = False
    
    return all_exist


def check_env_file():
    """Check for .env file."""
    print_header("Checking Environment Configuration")
    
    if os.path.exists('.env'):
        print_success(".env file exists")
        
        # Check if SECRET_KEY is set
        with open('.env', 'r') as f:
            content = f.read()
            if 'SECRET_KEY=' in content and 'your-secret-key' not in content:
                print_success("SECRET_KEY is configured")
            else:
                print_warning("SECRET_KEY might not be set properly")
                print("  Run: python -c \"import secrets; print(secrets.token_hex(32))\"")
    else:
        print_warning(".env file not found (required for deployment)")
        print("  Copy .env.example to .env and configure")


def check_database():
    """Check if database is initialized."""
    print_header("Checking Database")
    
    if os.path.exists('instance/agrifarma.db') or os.path.exists('agrifarma.db'):
        print_success("Database file exists")
    else:
        print_warning("Database not initialized")
        print("  Run: flask --app app.py init-db")


def check_migrations():
    """Check for database migrations."""
    print_header("Checking Database Migrations")
    
    if os.path.exists('migrations'):
        print_success("Migrations folder exists")
    else:
        print_warning("Migrations not initialized")
        print("  Run: flask db init")


def run_tests():
    """Run test suite."""
    print_header("Running Tests")
    
    try:
        result = subprocess.run(
            ['pytest', '-v', '--tb=short'],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print_success("All tests passed!")
            # Print test summary
            lines = result.stdout.split('\n')
            for line in lines:
                if 'passed' in line.lower():
                    print(f"  {line.strip()}")
        else:
            print_error("Some tests failed")
            print(result.stdout[-500:])  # Last 500 chars
            
        return result.returncode == 0
    except FileNotFoundError:
        print_warning("pytest not found. Skipping tests.")
        print("  Install: pip install pytest")
        return True
    except subprocess.TimeoutExpired:
        print_error("Tests timed out")
        return False


def check_dependencies():
    """Check if all dependencies are installed."""
    print_header("Checking Dependencies")
    
    try:
        result = subprocess.run(
            ['pip', 'check'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print_success("All dependencies are compatible")
        else:
            print_error("Dependency conflicts found")
            print(result.stdout)
            
        return result.returncode == 0
    except:
        print_warning("Could not check dependencies")
        return True


def check_git_status():
    """Check git status."""
    print_header("Checking Git Status")
    
    try:
        # Check if git is initialized
        if not os.path.exists('.git'):
            print_warning("Git not initialized")
            print("  Run: git init")
            return True
        
        # Check for uncommitted changes
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            capture_output=True,
            text=True
        )
        
        if result.stdout.strip():
            print_warning("Uncommitted changes detected")
            print("  Run: git add . && git commit -m 'Prepare for deployment'")
        else:
            print_success("All changes committed")
            
        return True
    except FileNotFoundError:
        print_warning("Git not found")
        return True


def check_security():
    """Check for basic security issues."""
    print_header("Security Check")
    
    issues = []
    
    # Check if .env is in .gitignore
    if os.path.exists('.gitignore'):
        with open('.gitignore', 'r') as f:
            if '.env' in f.read():
                print_success(".env is in .gitignore")
            else:
                print_error(".env is NOT in .gitignore!")
                issues.append(".env not in .gitignore")
    
    # Check if DEBUG is False in production config
    if os.path.exists('config.py'):
        with open('config.py', 'r') as f:
            content = f.read()
            if 'ProductionConfig' in content and 'DEBUG = False' in content:
                print_success("DEBUG is False in production")
            else:
                print_warning("Verify DEBUG is False in ProductionConfig")
    
    # Check for hardcoded secrets
    print("Checking for hardcoded secrets...")
    suspicious_files = []
    
    for root, dirs, files in os.walk('.'):
        # Skip virtual environment and git
        dirs[:] = [d for d in dirs if d not in ['venv', 'env', '.git', '__pycache__', 'node_modules']]
        
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read().lower()
                    if any(keyword in content for keyword in ['password = "', 'secret_key = "', 'api_key = "']):
                        if filepath not in suspicious_files:
                            suspicious_files.append(filepath)
    
    if suspicious_files:
        print_warning(f"Found {len(suspicious_files)} files with potential hardcoded secrets:")
        for file in suspicious_files[:5]:  # Show first 5
            print(f"  - {file}")
    else:
        print_success("No obvious hardcoded secrets found")
    
    return len(issues) == 0


def generate_summary():
    """Generate deployment summary."""
    print_header("Deployment Summary")
    
    print("\n📝 Pre-Deployment Checklist:")
    print("  1. ✅ Create .env file with SECRET_KEY")
    print("  2. ✅ Initialize database: flask init-db")
    print("  3. ✅ Create admin user: flask create-admin")
    print("  4. ✅ Seed demo data: flask seed-data")
    print("  5. ✅ Run tests: pytest -v")
    print("  6. ✅ Commit all changes: git add . && git commit")
    print("  7. ✅ Push to GitHub: git push origin main")
    
    print("\n🚀 Deployment Options:")
    print("  • Render.com: gunicorn app:app")
    print("  • PythonAnywhere: Use wsgi.py")
    print("  • Heroku: Procfile included")
    
    print("\n📚 Documentation:")
    print("  • README.md - Full project documentation")
    print("  • DEPLOYMENT_CHECKLIST.md - Detailed checklist")
    print("  • ERROR_HANDLING_DOCUMENTATION.md - Error handling guide")
    print("  • ANALYTICS_DOCUMENTATION.md - Analytics guide")
    
    print("\n🎯 Next Steps:")
    print("  1. Choose deployment platform (Render, PythonAnywhere, Heroku)")
    print("  2. Follow DEPLOYMENT_CHECKLIST.md")
    print("  3. Set environment variables on platform")
    print("  4. Deploy and test")
    print("  5. Initialize database on production")
    print("  6. Capture screenshots for submission")


def main():
    """Main function."""
    print("\n" + "🌾" * 30)
    print("  AgriFarma Deployment Preparation")
    print("🌾" * 30)
    
    checks = [
        ("Python Version", check_python_version),
        ("Required Files", check_files_exist),
        ("Environment Config", check_env_file),
        ("Database", check_database),
        ("Migrations", check_migrations),
        ("Dependencies", check_dependencies),
        ("Git Status", check_git_status),
        ("Security", check_security),
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print_error(f"{name} check failed: {str(e)}")
            results[name] = False
    
    # Run tests last (optional)
    print("\nRun tests? (y/n): ", end="")
    if input().lower() == 'y':
        results["Tests"] = run_tests()
    
    # Generate summary
    generate_summary()
    
    # Final verdict
    print_header("Final Verdict")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"\nChecks Passed: {passed}/{total}")
    
    if all(results.values()):
        print("\n✅ Your application is ready for deployment!")
        print("   Follow DEPLOYMENT_CHECKLIST.md for next steps.")
    elif passed >= total * 0.7:  # 70% passed
        print("\n⚠️  Most checks passed. Review warnings before deploying.")
    else:
        print("\n❌ Please fix the errors before deploying.")
    
    print("\n" + "=" * 60)


if __name__ == '__main__':
    main()
