import os
from tortoise import Tortoise

TORTOISE_ORM = {
    "connections": {
        "default": os.getenv("DB_URL", "postgres://postgres:postgres@localhost:5432/polywarren")
    },
    "apps": {
        "models": {
            "models": ["shared.models", "aerich.models"],
            "default_connection": "default",
        }
    },
}


async def init_db() -> None:
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas(safe=True)


async def close_db() -> None:
    await Tortoise.close_connections()
