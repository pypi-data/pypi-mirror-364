import sys
from .gen import create_django_app

def main():
    if len(sys.argv) != 2:
        print("Usage: create-django nom_de_mon_app")
        sys.exit(1)
    app_name = sys.argv[1]
    create_django_app(app_name)

if __name__ == "__main__":
    main()
