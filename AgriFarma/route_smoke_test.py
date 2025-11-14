from agrifarma import create_app
from agrifarma.extensions import db

app = create_app('testing')
with app.app_context():
    db.create_all()
    client = app.test_client()
    paths = ['/', '/blog/', '/forum/', '/marketplace/']
    for p in paths:
        try:
            r = client.get(p)
            print(f'{p} -> {r.status_code}')
        except Exception as e:
            print(f'{p} -> ERROR: {e}')
