import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.core.config import settings
from app.db.base import Base
from app.db.models.endpoint import Endpoint  # noqa: F401
from app.db.models.enrollment_token import EnrollmentToken  # noqa: F401
from app.db.models.inventory_bitlocker_volume import InventoryBitlockerVolume  # noqa: F401
from app.db.models.inventory_category_state import InventoryCategoryState  # noqa: F401
from app.db.models.inventory_disk import InventoryDisk  # noqa: F401
from app.db.models.inventory_firewall_profile import InventoryFirewallProfile  # noqa: F401
from app.db.models.inventory_hardware import InventoryHardware  # noqa: F401
from app.db.models.inventory_local_user import InventoryLocalUser  # noqa: F401
from app.db.models.inventory_network_adapter import InventoryNetworkAdapter  # noqa: F401
from app.db.models.inventory_network_address import InventoryNetworkAddress  # noqa: F401
from app.db.models.inventory_os import InventoryOS  # noqa: F401
from app.db.models.inventory_security_status import InventorySecurityStatus  # noqa: F401
from app.db.models.inventory_service import InventoryService  # noqa: F401
from app.db.models.inventory_software import InventorySoftware  # noqa: F401
from app.db.models.inventory_sync_log import InventorySyncLog  # noqa: F401
from app.db.models.inventory_volume import InventoryVolume  # noqa: F401
from app.db.models.inventory_windows_update import InventoryWindowsUpdate  # noqa: F401
from app.db.models.organization import Organization  # noqa: F401
from app.db.models.user import User  # noqa: F401

# this is the Alembic Config object, which provides access to the values
# within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata from DB base models for autogenerate detection
target_metadata = Base.metadata

# Inject Settings database URL directly into context configuration
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL and not an Engine.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine and associate a connection with the context.
    """
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = settings.DATABASE_URL

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
