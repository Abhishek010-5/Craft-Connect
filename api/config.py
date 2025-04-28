import os
from dotenv import load_dotenv

load_dotenv()

DB_ADMIN = os.getenv("DB_ADMIN")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = os.getenv("DB_PORT")

DB_URI = f'postgres://{DB_ADMIN}:{DB_PASSWORD}.c.{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require'

JWT_EXPIRY_MINUTES = int(os.getenv("JWT_EXPIRY_MINUTES"))
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")

PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL =  os.getenv("MAIL")

ADMIN_KEY = os.getenv("ADMIN_KEY")

SECRET_KEY = os.getenv("SECRET_KEY")

