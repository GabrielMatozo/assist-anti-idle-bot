import sys
import traceback
from src.app import AntiIdleApp


def main():
    try:
        app = AntiIdleApp()
        app.run()
    except Exception:
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
