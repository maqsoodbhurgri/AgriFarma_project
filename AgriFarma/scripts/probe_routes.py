from agrifarma import create_app

app = create_app('testing')
with app.app_context():
    c = app.test_client()
    paths = ['/', '/index', '/dashboard']
    for p in paths:
        try:
            r = c.get(p, follow_redirects=True)
            print(f"{p} -> {r.status_code} len:{len(r.get_data(as_text=True))}")
        except Exception as e:
            print(f"{p} -> ERROR: {e}")
