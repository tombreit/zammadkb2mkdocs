#!/usr/bin/env python3

"""
Converts the JSON output from export_kb.py to a Markdown file for MkDocs.
"""

import json
import re
import shutil
import logging
from dataclasses import dataclass, field
from pathlib import Path

from markdownify import markdownify as md
import frontmatter as pyfrontmatter
# import pypandoc

from .config import Config

logger = logging.getLogger(__name__)


LANGUAGES = {
    1: "en",
    35: "de",
}


@dataclass
class ConvertResult:
    articles: int = 0
    languages: set = field(default_factory=set)
    tags: set = field(default_factory=set)


convert_result = ConvertResult()


def slugify(text: str) -> str:
    """Convert text to URL-friendly slug."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[-\s]+", "-", text).strip("-")
    return text


def html_to_markdown(html_content: str) -> str:
    """Convert HTML to Markdown using pypandoc."""
    try:
        # return pypandoc.convert_text(
        #     html_content,
        #     to="markdown_strict",
        #     format="html",
        #     extra_args=["--wrap=none"],
        # )
        return md(html_content)
    except Exception as e:
        logger.error(f"Error converting HTML to Markdown: {e}")
        return html_content


def convert_to_mkdocs(json_file: Path, output_dir: Path) -> None:
    """Convert JSON entries to individual Markdown files."""

    with json_file.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if output_dir.exists():
        shutil.rmtree(output_dir)

    output_dir.mkdir(parents=True)

    for answer_id, answer_item in data.items():
        for language_id, translation_item in answer_item["translations"].items():
            language_id = int(language_id)
            language = LANGUAGES[language_id]
            title = translation_item["title"]
            content = translation_item["content"]

            convert_result.languages.add(language)

            # if answer_item["answer_content"] == "":
            #     logger.warning(f"Skipping entry with no content: {answer_item['answer_title']}")
            #     continue

            # filename = f"{answer_id}-{slugify(title)}.{language}.md"
            filename = f"{answer_id}.{language}.md"
            markdown_content = html_to_markdown(content)

            # Add title to markdown content
            markdown_content = f"# {title}\n\n" + markdown_content

            # Add markdown frontmatter via python-frontmatter package
            category = answer_item.get("category")
            tags = [category.get("title"), category.get("parent_title")]

            frontmatter = {"tags": tags}
            _markdown_content = pyfrontmatter.Post(markdown_content, **frontmatter)
            markdown_content = pyfrontmatter.dumps(_markdown_content)

            # Tags statistics
            convert_result.tags.update(tags)

            # Write markdown content to file
            output_path = output_dir / filename
            with output_path.open("w", encoding="utf-8") as f:
                f.write(markdown_content)

            logger.debug(f"Created: {output_path}")
            convert_result.articles += 1


def add_tags_page(docs_dir: Path) -> None:
    """Create a tags page for MkDocs."""

    tags_content = """
# Tags

<!-- material/tags -->

"""

    tags_path = docs_dir / "tags.md"
    with tags_path.open("w", encoding="utf-8") as f:
        f.write(tags_content)

    logger.info(f"Created tags page: {tags_path}")


def copy_images(images_dir: str, output_dir: Path) -> None:
    """Copy images to the output directory."""

    images_dir = Path(images_dir)
    if not images_dir.exists():
        logger.error(f"Images directory not found: {images_dir}")
        return

    logger.info(f"Copying images from {images_dir} to {output_dir}...")
    images_output_dir = output_dir / "images"
    shutil.copytree(images_dir, images_output_dir, dirs_exist_ok=True)


def convert(config: Config) -> None:
    logger.debug(
        f"Converting JSON {config.json_imgfixed_path} to MkDocs markdown files in {config.docs_kb_dir}"
    )

    convert_to_mkdocs(config.json_imgfixed_path, config.docs_kb_dir)
    add_tags_page(config.docs_dir)
    copy_images(config.img_dir, config.docs_dir)

    return convert_result
