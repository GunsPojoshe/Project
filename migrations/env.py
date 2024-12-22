#env.py#
from flask import current_app
from alembic import context
from sqlalchemy import create_engine, pool
from logging.config import fileConfig

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# Добавляем MetaData из текущего приложения Flask
target_metadata = current_app.extensions['migrate'].db.metadata


def run_migrations_online():
    """Run migrations in 'online' mode for multiple binds."""
    db_binds = current_app.config.get('SQLALCHEMY_BINDS', {})
    db_binds['default'] = current_app.config['SQLALCHEMY_DATABASE_URI']

    for bind_key, url in db_binds.items():
        if url is None:
            continue  # Пропускаем неверные или пустые подключения

        connectable = create_engine(url, poolclass=pool.NullPool)

        with connectable.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                compare_type=True,
            )

            print(f"Running migrations for bind: {bind_key}")
            with context.begin_transaction():
                context.run_migrations()


run_migrations_online()
