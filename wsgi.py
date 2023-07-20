import sys

from asteria.api import create_app
from asteria.settings import ASTERIA_HOST, ASTERIA_PORT

app = create_app()

if __name__ == "__main__":
    try:
        import werkzeug
    except ImportError:
        sys.exit("Werkzeug package not installed.")

    werkzeug.run_simple(ASTERIA_HOST, ASTERIA_PORT, app)
