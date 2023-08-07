import os

SECRET_KEY = os.environ.get("SECRET_KEY", "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7")
DB_SERVER = os.environ.get("DB_SERVER", "localhost")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "admin")
DB_NAME = os.environ.get("DB_NAME", "blogging")
DB_TEST_NAME = os.environ.get("DB_TEST_NAME", "testing")
RABBITMQ_SERVER = os.environ.get("RABBITMQ_SERVER", "localhost")
RABBITMQ_USER = os.environ.get("RABBITMQ_USER", "admin")
RABBITMQ_PASSWORD = os.environ.get("RABBITMQ_PASSWORD", "admin")
RABBITMQ_PORT = int(os.environ.get("RABBITMQ_PORT", "5672"))
