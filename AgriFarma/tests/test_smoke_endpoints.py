import pytest
from agrifarma import create_app

@pytest.fixture(scope="module")
def app():
    app = create_app('development')
    app.config.update(TESTING=True)
    return app

@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.mark.parametrize("path", [
    "/",
    "/blog/",
    "/marketplace/",
    "/consultancy/",
    "/forum/",
])
def test_endpoints_ok(client, path):
    rv = client.get(path)
    assert rv.status_code in (200, 302)
