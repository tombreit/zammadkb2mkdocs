import argparse
import logging
import io
import dataclasses
from pathlib import Path
from typing import Dict, Optional
from pprint import pprint

from .config import Config
from .export import export_to_json
from .images import fix_images
from .convert import convert
from . import set_loglevel

logger = logging.getLogger(__name__)


def create_parser():
    parser = argparse.ArgumentParser(
        description="Export Zammad Knowledge Base to MkDocs project"
    )

    parser.add_argument(
        "db_path",
        type=Path,
        help="SQLite database path",
    )
    parser.add_argument(
        "--zammad-fqdn",
        type=str,
        help="Zammad attachments base API URL, eg. https://zammad.example.com/api/v1/attachments/",
        required=True,
    )
    parser.add_argument(
        "--loglevel",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the log level",
    )

    return parser


class Exporter:
    def __init__(self, config: Config):
        self.config = config
        self.data: Optional[Dict] = None

    def export(self) -> dict:
        """Run full export pipeline."""

        logger.info("Starting export process...")
        logger.info(f"Exporting {self.config.db_path} to {self.config.docs_dir}")

        # Step 1: Export from DB to JSON
        self.data = export_to_json(self.config.db_path, self.config.json_path)

        # Step 2: Process images
        fixed_images = fix_images(self.config)

        # Step 3: Convert to MkDocs
        articles = convert(self.config)

        return {
            "images": dataclasses.asdict(fixed_images),
            "convert": dataclasses.asdict(articles),
        }


def main() -> int:
    """Run complete export pipeline"""
    parser = create_parser()
    args = parser.parse_args()

    set_loglevel(args.loglevel)

    config = Config(
        db_path=args.db_path, zammad_fqdn=args.zammad_fqdn, loglevel=args.loglevel
    )

    exporter = Exporter(config)
    result = exporter.export()

    pprint_buffer = io.StringIO()
    pprint(result, indent=2, stream=pprint_buffer)
    logger.info(f"Export result: {pprint_buffer.getvalue()}")
