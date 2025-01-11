import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, Optional


@contextmanager
def sqlite_connection(db_path: Path):
    """Context manager for SQLite database connections."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def execute_query(db_path: Path, query: str) -> Optional[Dict]:
    """Execute SQL query and return data."""
    try:
        with sqlite_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = [dict(row) for row in cursor.fetchall()]

            return rows

    except sqlite3.Error as e:
        raise f"Database error: {e}"


def validate_sqlite_file(file_path: Path) -> bool:
    """Validate if file is a SQLite database using built-in sqlite3."""

    # if file_path.suffix.lower() not in [".db", ".sqlite", ".sqlite3"]:
    #     return False

    try:
        with sqlite_connection(file_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT sqlite_version()")
            return
    except sqlite3.Error as e:
        raise f"SQLite validation error: {e}"


def convert_cid_to_img_id(cid: str, db_path: Path, zammad_fqdn: str) -> str:
    """
    Convert a Content-ID (CID) from a Knowledge Base image link to its corresponding image ID in the Zammad database.

    Args:
        cid (str): The Content-ID portion of the image link (UUID format)
        zammad_dbfile (Union[str, Path]): Path to the Zammad SQLite database file

    Returns:
        str: The image ID from the stores table if found, empty string otherwise

    Example:
        >>> convert_cid_to_img_id("94d513bb-abee-4c8a-8132-0f2923118a95", "zammad.db")
        "26880"

    Note:
        The function searches the stores table in the Zammad database for a record where
        the preferences field contains the full Content-ID constructed from the input CID.

    Convert CID image link to image ID, eg.:
    cid:KnowledgeBase::Answer::Translation::Content_body.94d513bb-abee-4c8a-8132-0f2923118a95@zammad.example.org -> 26880

    The cid is part of the "preferences" filed in the "stores" table and the img_id is the "id" field.
    """

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        full_cid = (
            f"KnowledgeBase::Answer::Translation::Content_body.{cid}@{zammad_fqdn}"
        )
        query = "SELECT id FROM stores WHERE preferences LIKE ?"
        cursor.execute(query, (f"%Content-ID: {full_cid}%",))
        result = cursor.fetchone()
        return str(result[0]) if result else ""
