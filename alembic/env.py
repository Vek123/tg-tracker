# migrations/env.py
from logging.config import fileConfig
import sqlalchemy as sa
from alembic import context
from alembic.ddl.impl import DefaultImpl

from db.core import Model, db_manager

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Model.metadata

# YDB-specific implementation
class YDBImpl(DefaultImpl):
    __dialect__ = "yql"

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
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
    """Run migrations in 'online' mode."""

    with db_manager.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        ctx = context.get_context()
        ctx._version = sa.Table(
            ctx.version_table,
            sa.MetaData(),
            sa.Column("version_num", sa.String(32), nullable=False),
            sa.Column("id", sa.Integer(), nullable=True, primary_key=True),
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()