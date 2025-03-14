import os
import random
import sqlite3 as sql
from pathlib import Path
from typing import Optional

import pytest
from faker import Faker

from crow import db
from crow.model import Page

fake = Faker()


def fake_page(
    title: Optional[str] = None,
    source_path: Optional[str] = None,
    toc_path: Optional[str] = None,
    modified: Optional[float] = None,
) -> Page:
    return Page(
        title=title if title is not None else fake.sentence(),
        source_path=source_path
        if source_path is not None
        else Path(fake.file_path(depth=3, extension="html", file_system_rule="windows")),
        toc_path=toc_path if toc_path is not None else fake.file_path(depth=5, extension="", file_system_rule="linux"),
        modified=modified if modified is not None else random.random() * 100000,
    )


pages = [fake_page() for _ in range(10)]


def check_page_lists_eq(list1: list[Page], list2: list[Page]) -> bool:
    # Use verbose implementation for easier debugging
    def title(x: Page) -> str:
        return x.title

    return all(page1 == page2 for page1, page2 in zip(sorted(list1, key=title), sorted(list2, key=title)))


def test_init():
    # Create database
    db.init("test.sqlite")
    # Check that file was created
    assert os.path.exists("test.sqlite"), "Expected database file to be created on disk"


def test_init_overwrite():
    with open("test.sqlite", "wb") as f:
        f.write(b"foo")
    db.init("test.sqlite")
    assert os.path.exists("test.sqlite"), "Expected database file to be created on disk"
    with open("test.sqlite", "rb") as f:
        db_cnt = f.read()
    assert db_cnt != b"foo", "Expected database to be overwritten on db.init"


def test_structure():
    # Check that it has the right structure
    with db.connect() as (_, cursor):
        cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table'")
        rows = cursor.fetchall()

    assert len(rows) == 1, "There must be exactly one table"
    row = rows[0]
    assert row["name"] == "pages", "Expected 'pages' table to be created"
    assert (
        row["sql"]
        == "CREATE TABLE pages (title TEXT PRIMARY KEY NOT NULL, source_path TEXT, toc_path TEXT, modified REAL) STRICT"
    ), "Expected following database structure"


def test_empty():
    with db.connect() as (_, cursor):
        cursor.execute("SELECT count(*) FROM pages")
        count = next(iter(cursor.fetchone().values()))  # get first element
    assert count == 0, "No data shall be inserted on startup"


def test_pages_add():
    db.pages_clear()

    # Insert fake pages
    db.pages_add(pages)

    # Validate inserted data
    with db.connect() as (_, cursor):
        # jinx the order for good measure
        cursor.execute("SELECT * FROM pages ORDER BY modified")
        rows = cursor.fetchall()
    pages_retrieved = [Page(**row) for row in rows]
    assert check_page_lists_eq(pages_retrieved, pages)


def test_connect_read_ok():
    db.pages_clear()
    db.pages_add(pages)

    with db.connect() as (_, cursor):
        cursor.execute("SELECT * FROM pages LIMIT 5")
        rows = cursor.fetchall()
    assert len(rows) == 5, "5 pages must have been fetched"


def test_connect_read_bad_query():
    # Check that incorrect queries raise appropriate error and close connection
    with pytest.raises(sql.OperationalError), db.connect() as (conn, cursor):
        conn_to_check = conn
        cursor.execute("SELECT * FROM pages WHERE foo = bar LIMIT 1")

    # Check that connections are closed after faulty read
    with pytest.raises(sql.ProgrammingError):
        conn_to_check.execute("SELECT * FROM pages LIMIT 1")


def test_connect_write_ok():
    db.pages_clear()
    db.pages_add(pages)

    new_page = fake_page()
    with db.connect(write=True) as (_, cursor):
        cursor.execute(
            "INSERT INTO pages (title, source_path, toc_path, modified) VALUES (?, ?, ?, ?)",
            (new_page.title, str(new_page.source_path), new_page.toc_path, new_page.modified),
        )

    # Check that new data appeared in db
    with db.connect() as (_, cursor):
        cursor.execute("SELECT count(*) FROM pages")
        count = next(iter(cursor.fetchone().values()))
    assert count == len(pages) + 1, "Expected value to be added"


def test_connect_write_bad_readonly():
    db.pages_clear()
    db.pages_add(pages)

    new_page = fake_page()
    # Check that attempts to write without the write=True fail with OperationalError
    with pytest.raises(sql.OperationalError), db.connect() as (conn, cursor):
        conn_to_check = conn
        cursor.execute(
            "INSERT INTO pages (title, source_path, toc_path, modified) VALUES (?, ?, ?, ?)",
            (new_page.title, str(new_page.source_path), new_page.toc_path, new_page.modified),
        )

    # Check that old connection is closed
    with pytest.raises(sql.ProgrammingError):
        conn_to_check.execute("SELECT * FROM pages LIMIT 1")

    # Check that database is intact
    with db.connect() as (_, cursor):
        # jinx the order for good measure
        cursor.execute("SELECT * FROM pages ORDER BY modified")
        rows = cursor.fetchall()
    pages_retrieved = [Page(**row) for row in rows]
    assert check_page_lists_eq(pages_retrieved, pages)


def test_connect_write_bad_values():
    db.pages_clear()
    db.pages_add(pages)

    new_page = fake_page()
    # Check that attempts to write bad values fail with IntegrityError
    with pytest.raises(sql.IntegrityError), db.connect(write=True) as (conn, cursor):
        conn_to_check = conn
        cursor.execute(
            "INSERT INTO pages (title, source_path, toc_path, modified) VALUES (?, ?, ?, ?)",
            (new_page.title, str(new_page.source_path), new_page.toc_path, new_page.modified),
        )
        # Now insert bad data
        cursor.execute(
            "INSERT INTO pages (title, source_path, toc_path, modified) VALUES (?, ?, ?, ?)",
            (new_page.title + "a", str(new_page.source_path), new_page.toc_path, "foo"),
        )

    # Check that old connection is closed
    with pytest.raises(sql.ProgrammingError):
        conn_to_check.execute("SELECT * FROM pages LIMIT 1")

    # Check that database is intact
    with db.connect() as (_, cursor):
        # jinx the order for good measure
        cursor.execute("SELECT * FROM pages ORDER BY modified")
        rows = cursor.fetchall()
    pages_retrieved = [Page(**row) for row in rows]
    assert check_page_lists_eq(pages_retrieved, pages)


def test_get_by_title():
    db.pages_clear()
    db.pages_add(pages)

    page = pages[0]
    page_retrieved = db.page_get_by_title(page.title)

    # Make sure that objects are different
    assert page is not page_retrieved, "Retrieving records from db must create new instances"
    assert page == page_retrieved, "Failed to fetch the right page"


def test_get_by_title_missing():
    db.pages_clear()
    db.pages_add(pages)

    page_retrieved = db.page_get_by_title("foo")  # there ain't no way we get book with this title
    assert page_retrieved is None, "Non-existent page must return None"


def test_update_modified():
    db.pages_clear()
    db.pages_add(pages)

    page_new = Page.model_validate(pages[0])
    page_new.modified = 420
    db.page_update_modified(page_new)

    page_retrieved = db.page_get_by_title(page_new.title)

    # Make sure that objects are different
    assert page_new is not page_retrieved, "Retrieving records from db must create new instances"
    assert page_new == page_retrieved, "Failed to update modified time"


def test_db_remove():
    assert os.path.exists("test.sqlite"), "Expected database to persist until the end of tests"
    os.remove("test.sqlite")
