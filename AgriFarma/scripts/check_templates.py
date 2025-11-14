import os
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(ROOT, 'templates')

loader = FileSystemLoader(TEMPLATES_DIR)
env = Environment(loader=loader, autoescape=True)

errors = []
loaded = []
legacy_extends = []

for base, _, files in os.walk(TEMPLATES_DIR):
    for fname in files:
        if not fname.endswith('.html'):
            continue
        full = os.path.join(base, fname)
        rel = os.path.relpath(full, TEMPLATES_DIR).replace('\\', '/')
        try:
            # Check for legacy extends markers
            try:
                src, _, _ = loader.get_source(env, rel)
            except Exception:
                src = ''
            if 'extends "layouts/base' in src or "extends 'layouts/base" in src:
                legacy_extends.append(rel)
            # Load to ensure includes/extends resolve
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
