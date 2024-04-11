import os
from pathlib import Path
from dotenv import load_dotenv

from dataclasses import dataclass
from sqlalchemy.engine import URL


load_dotenv()


@dataclass
class settings:
    BASE_URL = Path(__file__).parent.parent.resolve()

    BOT_TOKEN: str = os.getenv('BOT_TOKEN')

    DB_USERNAME: str = os.getenv('DB_USERNAME')
    DB_PASSWORD: str = os.getenv('DB_PASSWORD')
    DB_NAME: str = os.getenv('DB_NAME')
    DB_HOST: str = os.getenv('DB_HOST')
    DB_PORT: int = str(os.getenv('DB_PORT'))


def get_db_url():
    return URL.create(
        drivername='postgresql+asyncpg',
        username=settings.DB_USERNAME,
        password=settings.DB_PASSWORD,
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        database=settings.DB_NAME
    )