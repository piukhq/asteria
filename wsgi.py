import sys

from asteria.api import create_app
from asteria.settings import settings

app = create_app()

if __name__ == "__main__":
    try:
        import werkzeug
    except ImportError:
        sys.exit("Werkzeug package not installed.")

    werkzeug.run_simple(settings.ASTERIA_HOST, settings.ASTERIA_PORT, app)
