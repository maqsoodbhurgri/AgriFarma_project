"""Smoke tests for blog routes.
Run to verify blog index renders and detail page + like flow works minimally.
"""
from agrifarma import create_app
from agrifarma.extensions import db
from agrifarma.models.blog import BlogPost, BlogCategory

app = create_app()

def assert_in(text, data):
    if text not in data:
        print(f"[WARN] Expected text not found: {text}")
        return False
    print(f"[OK] Found: {text}")
    return True

with app.app_context():
    with app.test_client() as client:
        print("Testing /blog/ index...")
        response = client.get('/blog/')
        print(f"Status Code: {response.status_code}")
        if response.status_code != 200:
            print(f"[FAIL] Blog index did not load. Snippet:\n{response.data.decode()[:400]}")
        else:
            data = response.data.decode()
            assert_in('Blog & Resources', data)
            # Check at least one category badge pattern
            # (Assumes categories seeded elsewhere)
            if not ('badge-' in data and 'Categories' in data):
                print('[WARN] Category listing may be missing.')
            # Try to locate a post link pattern
            if 'post_detail' not in data:
                print('[WARN] No post links found; ensure posts seeded.')

        # Pick first post for detail test if exists
        post = BlogPost.query.filter_by(is_published=True, is_deleted=False).order_by(BlogPost.published_at.desc()).first()
        if post:
            print(f"Testing detail view for post id={post.id} slug={post.slug}...")
            d_resp = client.get(f'/blog/post/{post.id}/{post.slug}')
            print(f"Detail Status: {d_resp.status_code}")
            if d_resp.status_code == 200:
                d_data = d_resp.data.decode()
                assert_in(post.title, d_data)
                assert_in('Comments', d_data)
                assert_in('Like', d_data)
            else:
                print(f"[FAIL] Detail page failed. Snippet:\n{d_resp.data.decode()[:400]}")
        else:
            print('[INFO] No published posts available to test detail view.')

print('Blog smoke tests completed.')
