# SPDX-FileCopyrightText: Thomas Breitner
#
# SPDX-License-Identifier: EUPL-1.2

import logging


# Configure root logger once
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def set_loglevel(level: str) -> None:
    """Update root logger level after initial configuration"""
    logging.getLogger().setLevel(level)


__all__ = ["set_loglevel"]
