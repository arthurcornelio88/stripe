import os
import sys
from pathlib import Path
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# === Setup PYTHONPATH to access app/
sys.path.append(str(Path(__file__).resolve().parents[1]))

# === ENV loader (DEV/PROD)
from app.utils.env_loader import load_project_env
ENV = load_project_env()

# === Alembic config
config = context.config

# === Logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# === SQLAlchemy models
from app.db.base import Base
from app import models  # force loading of all models
target_metadata = Base.metadata

# === Load DB variables from env (via load_project_env)
user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
host = os.getenv("POSTGRES_HOST", "localhost")
port = os.getenv("POSTGRES_PORT", "5434")
db = os.getenv("POSTGRES_DB")

# === Inject sqlalchemy.url dynamically
config.set_main_option(
    "sqlalchemy.url",
    f"postgresql://{user}:{password}@{host}:{port}/{db}"
)

# === Migration runners
def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

# === Run
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
