import secrets
import sys

def generate_django_env():
    secret = secrets.token_urlsafe(50)
    content = f"""SECRET_KEY={secret}
DEBUG=True
DB_NAME=mydb
DB_USER=postgres
DB_PASSWORD=admin
"""
    with open(".env", "w") as f:
        f.write(content)
    print("✅ Fichier .env généré pour Django !")

def generate_flask_env():
    secret = secrets.token_hex(32)
    content = f"""FLASK_ENV=development
SECRET_KEY={secret}
DEBUG=True
"""
    with open(".env", "w") as f:
        f.write(content)
    print("✅ Fichier .env généré pour Flask !")

def main():
    if len(sys.argv) < 2:
        print("Usage: envgen [django|flask]")
        return

    preset = sys.argv[1].lower()
    if preset == "django":
        generate_django_env()
    elif preset == "flask":
        generate_flask_env()
    else:
        print("❌ Preset non reconnu. Utilise : django | flask")

if __name__ == "__main__":
    main()
