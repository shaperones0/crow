"""
A module for managing SQLite database operations for Page objects.

This module provides functions to initialize, connect to, and interact with an SQLite database
designed to store Page objects. It includes CRUD operations for pages and handles database
connections via context managers for safe transaction handling.

Classes and functions interact with the `Page` model from the `.model` module, ensuring
data integrity and proper type handling. The module uses row factories to return query results
as dictionaries for easier conversion to Page instances.
"""

import sqlite3 as sql
from collections.abc import Iterable, Iterator
from contextlib import AbstractContextManager, contextmanager
from typing import Any

from .model import Page


def dict_factory(cur: sql.Cursor, row: sql.Row) -> dict[str, Any]:
    """Convert a SQLite row to a dictionary with column names as keys.

    Args:
        cur: The cursor used for the query.
        row: The raw SQLite row result.

    Returns:
        A dictionary mapping column names to their respective values.
    """
    return {col[0]: row[idx] for idx, col in enumerate(cur.description)}


sqlite_filename_global: str | None = None


def init(sqlite_filename: str) -> None:
    """Initialize the database and create required tables.

    This function sets up the SQLite database file, truncates any existing content,
    and ensures the `pages` table exists with the correct schema.

    Args:
        sqlite_filename: Path to the SQLite database file. Will be created if it doesn't exist.

    Raises:
        sqlite3.OperationalError: If there's an issue creating the database file or tables.
    """
    global sqlite_filename_global
    sqlite_filename_global = sqlite_filename

    # Clear database
    with open(sqlite_filename, "w") as _:
        pass

    # Ensure database structure
    with connect(write=True) as (_, cursor):
        # Create pages table
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS pages ("
            "title TEXT PRIMARY KEY NOT NULL, "
            "source_path TEXT, "
            "toc_path TEXT, "
            "modified REAL) STRICT"
        )


def connect(*, write: bool = False) -> AbstractContextManager[tuple[sql.Connection, sql.Cursor]]:
    """Context manager for database connections with automatic transaction handling.

    Yields a connection and cursor tuple. For write operations, changes are committed on exit.
    For read operations, transactions are rolled back to prevent lock contention.

    Args:
        write: If True, opens connection in read/write mode. Defaults to read-only.

    Yields:
        A tuple containing the active SQLite connection and cursor.

    Raises:
        sqlite3.Error: If connection or cursor creation fails.
    """

    @contextmanager
    def wrapper() -> Iterator[tuple[sql.Connection, sql.Cursor]]:
        uri = f"file:{sqlite_filename_global}" if write else f"file:{sqlite_filename_global}?mode=ro"
        connection = sql.connect(uri, autocommit=False, isolation_level=None, uri=True)
        try:
            connection.row_factory = dict_factory
            cursor = connection.cursor()
            try:
                yield connection, cursor
            except Exception:
                cursor.close()
                connection.rollback()
                raise
            else:
                cursor.close()
                if write:
                    connection.commit()
                else:
                    connection.rollback()
        finally:
            connection.close()

    return wrapper()


def page_get_by_title(title: str) -> Page | None:
    """Retrieve a page by its title.

    Args:
        title: The title of the page to fetch.

    Returns:
        A Page instance if found, otherwise None.
    """
    with connect() as (_, cursor):
        cursor.execute("SELECT * FROM pages WHERE title = ?", (title,))
        row = cursor.fetchone()
    return Page(**row) if row else None


def page_update_modified(page: Page) -> None:
    """Update the modification timestamp of a page.

    Args:
        page: The Page object containing the new modified timestamp.
    """
    with connect(write=True) as (_, cursor):
        cursor.execute("UPDATE pages SET modified = ? WHERE title = ?", (page.modified, page.title))


def pages_add(pages: Iterable[Page]) -> None:
    """Insert multiple pages into the database in a single transaction.

    Args:
        pages: An iterable of Page objects to add to the database.
    """
    pages_tuples = [(page.title, str(page.source_path), page.toc_path, page.modified) for page in pages]

    with connect(write=True) as (_, cursor):
        cursor.executemany(
            "INSERT INTO pages (title, source_path, toc_path, modified) VALUES (?, ?, ?, ?)", pages_tuples
        )


def pages_clear() -> None:
    """Delete all records from the pages table.

    Warning: This operation is irreversible and removes all page entries.
    """
    with connect(write=True) as (_, cursor):
        # noinspection SqlWithoutWhere
        cursor.execute("DELETE FROM pages")
