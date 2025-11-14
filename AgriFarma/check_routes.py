"""Check what routes are actually registered when app runs"""
from agrifarma import create_app

app = create_app()

print("\n" + "="*60)
print("CHECKING REGISTERED ROUTES")
print("="*60 + "\n")

auth_routes = []
all_routes = []

for rule in app.url_map.iter_rules():
    if not rule.rule.startswith('/static'):
        all_routes.append(rule.rule)
        if '/auth' in rule.rule:
            auth_routes.append(f"{rule.rule} - {list(rule.methods - {'OPTIONS', 'HEAD'})}")

print(f"Total routes registered: {len(all_routes)}\n")

if auth_routes:
    print(f"✓ AUTH ROUTES FOUND ({len(auth_routes)}):")
    for route in auth_routes[:10]:
        print(f"  - {route}")
else:
    print("✗ NO AUTH ROUTES FOUND!")
    print("\nFirst 10 routes:")
    for route in all_routes[:10]:
        print(f"  - {route}")

print("\n" + "="*60)
