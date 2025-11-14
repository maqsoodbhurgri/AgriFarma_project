"""
Simple test server - Direct run without reloader
"""
import os

# Clear any werkzeug environment variables
if 'WERKZEUG_RUN_MAIN' in os.environ:
    del os.environ['WERKZEUG_RUN_MAIN']
if 'WERKZEUG_SERVER_FD' in os.environ:
    del os.environ['WERKZEUG_SERVER_FD']

os.environ['FLASK_ENV'] = 'development'

from agrifarma import create_app

app = create_app('development')

if __name__ == '__main__':
    print("\n" + "="*60)
    print("  AGRIFARMA SERVER STARTING")
    print("="*60)
    print(f"\n  → Server URL: http://127.0.0.1:5000")
    print(f"  → Debug Mode: ON")
    print(f"  → Auto-reload: OFF (for stability)")
    print("\n  Open your browser and visit:")
    print("  http://127.0.0.1:5000")
    print("\n  Press Ctrl+C to stop")
    print("="*60 + "\n")
    
    # Run without reloader for stability
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=True,
        use_reloader=False,
        use_debugger=True,
        threaded=True
    )
