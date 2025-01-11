# zammadkb2mkdocs

## Features

- `zammad2mkdocs` takes a Zammad database file and converts the Zammad Knowledge Base to a `MkDocs` project.
- Converts Zammad source HTML to Markdown
- Converts multilanguage Knowledge Base to multilanguage MkDocs
- Downloads referenced images and adjusts the image links
- Grabs the Zammad Knowlege Base categories and converts them to MkDocs tags

**🔥 This is work in progress - no liability for nothing.**

## Requirements

- Zammad database must be available as a SQLite3 database file

## Usage

### Install

```bash
git clone git@github.com:tombreit/zammadkb2mkdocs.git
cd zammadkb2mkdocs
python3 -m venv .venv
source .venv/bin/activate
pytho3 -m pip install .
```

### Run

```bash
zammadkb2mkdocs path/to/zammad-sqlite-dbfile --zammad-fqdn zammad.example.org
```

### Result

The Zammad Knowlege Base articles as Markdown files in `./dist/docs`.

For your convenience, `mkdocs` will be installed with this package and you can view your new MkDcos knowledgebase base right now: 

```bash
mkdocs serve
```

## Notes

- Currently only used/tested with a Zammad Knowlege Base in EN and DE.
- If the given `zammad-fqdn` is not reachable image src attributes will not be fixed and no images will be downloaded.
