#!/usr/bin/env python3

# SPDX-FileCopyrightText: Thomas Breitner
#
# SPDX-License-Identifier: EUPL-1.2

import json
import logging
from pathlib import Path

from .db import execute_query


logger = logging.getLogger(__name__)


KNOWLEDGE_BASE_QUERY = """
    SELECT 
        knowledge_base_answers.id AS answer_id,
        knowledge_base_answer_translations.id AS translation_id,
        knowledge_base_answer_translations.title AS answer_title,
        knowledge_base_answer_translation_contents.body AS answer_content,
        knowledge_base_locales.system_locale_id AS locale,
        kcat.title AS category_title,
        knowledge_base_categories.parent_id AS parent_id,
        parent_cat_trans.title AS parent_title,
        kcat.category_id AS category_id
    FROM 
        knowledge_base_answers
        LEFT JOIN knowledge_base_answer_translations 
            ON knowledge_base_answers.id = knowledge_base_answer_translations.answer_id
        LEFT JOIN knowledge_base_answer_translation_contents 
            ON knowledge_base_answer_translations.content_id = knowledge_base_answer_translation_contents.id
        LEFT JOIN knowledge_base_locales 
            ON knowledge_base_answer_translations.kb_locale_id = knowledge_base_locales.id
        LEFT JOIN knowledge_base_categories 
            ON knowledge_base_answers.category_id = knowledge_base_categories.id
        LEFT JOIN knowledge_base_category_translations kcat 
            ON knowledge_base_categories.id = kcat.category_id
            AND kcat.kb_locale_id = knowledge_base_locales.id
        LEFT JOIN knowledge_base_categories parent_cat
            ON knowledge_base_categories.parent_id = parent_cat.id
        LEFT JOIN knowledge_base_category_translations parent_cat_trans
            ON parent_cat.id = parent_cat_trans.category_id
            AND parent_cat_trans.kb_locale_id = knowledge_base_locales.id
    ORDER BY 
        knowledge_base_answers.id,
        knowledge_base_answer_translations.id
"""


def massage_data(rows: list) -> list:
    """Transform raw data into a more structured format."""

    structured_data = {}
    for row in rows:
        answer_id = row["answer_id"]

        if answer_id not in structured_data:
            structured_data[answer_id] = {
                "category": {
                    "id": row["category_id"],
                    "title": row["category_title"],
                    "parent_id": row["parent_id"],
                    "parent_title": row["parent_title"],
                },
                "translations": {},
            }

        # Add translation for this locale
        structured_data[answer_id]["translations"][row["locale"]] = {
            "title": row["answer_title"],
            "content": row["answer_content"],
        }

    return structured_data


def export_to_json(db_path: Path, json_path: Path) -> Path:
    """Export SQLite data to JSON file."""

    raw_data = execute_query(db_path, KNOWLEDGE_BASE_QUERY)
    structured_data = massage_data(raw_data)

    try:
        with json_path.open("w", encoding="utf-8") as f:
            json.dump(structured_data, f, ensure_ascii=False, indent=2)
        logger.info(f"Successfully exported SQLite data to JSON {json_path}")
        return json_path
    except IOError as e:
        raise (f"Failed to write JSON file: {e}")
