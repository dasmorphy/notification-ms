import os
from dotenv import load_dotenv

load_dotenv()

def access():
    return {
        "DB": {
            "POSTGRESQL": {
                "USER": os.getenv('POSTGRESQL_USER'),
                "PASSWORD": os.getenv('POSTGRESQL_PASSWORD').strip("'"),
                "HOST": os.getenv('POSTGRESQL_HOST'),
                "PORT": os.getenv('POSTGRESQL_PORT'),
                "DB": os.getenv('POSTGRESQL_DB')
            },
            "REDIS": {
                "HOST": os.getenv('REDIS_HOST'),
                "PORT": os.getenv('REDIS_PORT'),
            },
            "SQLALCHEMY_ENGINE_OPTIONS": {
                "echo": False,
                "pool_recycle": 300,
                "pool_pre_ping": True
            }
        },
        "PASSWORDS": {
            "ENCRYPTION": os.getenv('ENCRYPTION').strip("'")
        }
    }

def access_mode():
    return access()
