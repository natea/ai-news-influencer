"""Database connection and initialization."""
import aiosqlite
from pathlib import Path

from src.database.models import SQL_SCHEMA


class Database:
    """Async SQLite database manager."""

    def __init__(self, db_path: str = "./data/app.db"):
        self.db_path = db_path
        self._connection: aiosqlite.Connection | None = None

    async def connect(self) -> aiosqlite.Connection:
        """Connect to the database."""
        # Ensure data directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        self._connection = await aiosqlite.connect(self.db_path)
        self._connection.row_factory = aiosqlite.Row
        return self._connection

    async def disconnect(self) -> None:
        """Close the database connection."""
        if self._connection:
            await self._connection.close()
            self._connection = None

    async def initialize(self) -> None:
        """Initialize the database schema."""
        if not self._connection:
            await self.connect()

        await self._connection.executescript(SQL_SCHEMA)
        await self._connection.commit()

    @property
    def connection(self) -> aiosqlite.Connection:
        """Get the current connection."""
        if not self._connection:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self._connection


# Global database instance
db = Database()


async def get_db() -> aiosqlite.Connection:
    """Dependency for getting database connection."""
    if not db._connection:
        await db.connect()
        await db.initialize()
    return db.connection
