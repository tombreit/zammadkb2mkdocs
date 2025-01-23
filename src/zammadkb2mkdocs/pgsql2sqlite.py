# SPDX-FileCopyrightText: Thomas Breitner
#
# SPDX-License-Identifier: EUPL-1.2

import sys
import re
import argparse
import tempfile
import subprocess
import itertools
import time
import threading
from pathlib import Path

from .config import Config


class PostgresToSQLite:
    def __init__(self, config: Config):
        self.config = config
        self.input_file = config.db_path
        self.output_db = config.dist_dir / "zammad.sqlite3"

    def prepare_sql(self) -> Path:
        """Transform PostgreSQL dump to SQLite compatible SQL with progress indication"""
        print("Starting SQL conversion...", end="", flush=True)
        patterns = [
            r"^SET .*?;$",
            r"^SELECT pg_catalog.*?;$",
            r"^CREATE SEQUENCE.*?;",
            r"^ALTER SEQUENCE.*?;",
            r"^CREATE( UNIQUE)? INDEX.*?;",
            r"^ALTER TABLE ONLY.*?;",
        ]
        conversions = [
            (r"^(CREATE TABLE) public\.", r"\1 ", re.MULTILINE),
            (r"^(INSERT INTO) public\.", r"\1 ", re.MULTILINE),
            (r"\s+without time zone", ""),
            (
                r"'([^']*)'::character varying",
                r"'\1'",
                re.IGNORECASE,
            ),  # Remove type cast from default values
            (
                r"character varying(\(\d+\))?",
                "TEXT",
                re.IGNORECASE,
            ),  # Convert varchar to TEXT
            (
                r"'([^']*)'::text",
                r"'\1'",
                re.IGNORECASE,
            ),  # Remove text type cast from defaults
            (r"\btext\b", "TEXT", re.IGNORECASE),
            (r"TEXT\[\]", "TEXT", re.IGNORECASE),  # Convert array type
            (
                r"DEFAULT '\{\}'\[\]",
                "DEFAULT ''",
                re.IGNORECASE,
            ),  # Convert array default
        ]
        total_ops = len(patterns) + len(conversions)
        ops_done = 0

        with open(self.input_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Remove PostgreSQL-specific statements
        for pattern in patterns:
            content = re.sub(pattern, "", content, flags=re.DOTALL | re.MULTILINE)
            ops_done += 1
            print(
                f"\rProgress: {ops_done}/{total_ops} transformations",
                end="",
                flush=True,
            )

        # Convert types and syntax
        for pattern, replacement, *flags in conversions:
            flags = flags[0] if flags else 0
            content = re.sub(pattern, replacement, content, flags=flags)
            print(".", end="", flush=True)
            ops_done += 1

        print(f"\nCompleted {ops_done} transformations.")

        with tempfile.NamedTemporaryFile(mode="w", suffix=".sql", delete=False) as tmp:
            tmp.write("BEGIN TRANSACTION;\n")
            tmp.write(content)
            tmp.write("\nCOMMIT;")
            return Path(tmp.name)

    def import_to_sqlite(self, sqlite_sql: Path):
        """Import SQL using sqlite3 shell for better error reporting with a spinner."""

        def show_spinner(stop_event):
            spinner = itertools.cycle(["|", "/", "-", "\\"])
            while not stop_event.is_set():
                sys.stdout.write(next(spinner))
                sys.stdout.flush()
                time.sleep(0.1)
                sys.stdout.write("\b")

        if Path(self.output_db).exists():
            Path(self.output_db).unlink()

        print("Importing to SQLite... ", end="", flush=True)
        stop_event = threading.Event()
        spinner_thread = threading.Thread(target=show_spinner, args=(stop_event,))
        spinner_thread.start()

        process = subprocess.run(
            ["sqlite3", str(self.output_db)],
            input=f".bail on\n.read {sqlite_sql}",
            text=True,
            capture_output=True,
        )

        stop_event.set()
        spinner_thread.join()
        print("\b", end="\n", flush=True)

        if process.returncode != 0:
            print(f"SQLite Error:\n{process.stderr}")
            raise Exception("SQLite import failed")


def main():
    if subprocess.run(["which", "sqlite3"], capture_output=True).returncode != 0:
        print("Error: sqlite3 command not found. Please install it and try again.")
        sys.exit(1)

    parser = argparse.ArgumentParser(
        description="Convert Zammad PostgreSQL dump to SQLite database"
    )

    parser.add_argument(
        "pg_dump_file",
        type=Path,
        help="SQLite database path",
    )
    args = parser.parse_args()

    config = Config(db_path=args.pg_dump_file)
    converter = PostgresToSQLite(config)
    try:
        print("Step 1: Apply PostgreSQL to SQLite conversion")
        sqlite_sql = converter.prepare_sql()
        print(f"SQLite-compatible SQL written to: {sqlite_sql}")

        print("Step 2: Import to SQLite")
        converter.import_to_sqlite(sqlite_sql)
        print(f"SQLite database created: {converter.output_db}")

        # Cleanup
        sqlite_sql.unlink()
    except Exception as e:
        print(f"Error during conversion: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
