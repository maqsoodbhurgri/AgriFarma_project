import os
import sys
from flask import current_app
from flask import Flask
from jinja2 import TemplateNotFound

# Ensure project root is on sys.path
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from agrifarma import create_app

app = create_app(os.getenv('FLASK_ENV') or 'development')

errors = []
loaded = []
legacy_extends = []

templates_dir = app.jinja_loader.searchpath[0]

with app.app_context():
    loader = app.jinja_env.loader
    env = app.jinja_env

    for base, _, files in os.walk(templates_dir):
        for fname in files:
            if not fname.endswith('.html'):
                continue
            full = os.path.join(base, fname)
            rel = os.path.relpath(full, templates_dir).replace('\\', '/')
            try:
                try:
                    src, _, _ = loader.get_source(env, rel)
                except Exception:
                    src = ''
                if 'extends "layouts/base' in src or "extends 'layouts/base" in src:
                    legacy_extends.append(rel)
                # Use Flask's env to load (has filters/macros registered)
                env.get_template(rel)
                loaded.append(rel)
            except TemplateNotFound as e:
                errors.append((rel, f'TemplateNotFound: {e}'))
            except Exception as e:
                errors.append((rel, f'{type(e).__name__}: {e}'))

print('LOADED:', len(loaded))
print('ERRORS:', len(errors))
for rel, msg in errors:
    print(' -', rel, '->', msg)

print('LEGACY_EXTENDS:', len(legacy_extends))
for rel in legacy_extends:
    print(' *', rel)
