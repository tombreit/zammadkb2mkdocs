# zammadkb2mkdocs

## Features

- `zammadkb2mkdocs` takes a Zammad database file and converts the Zammad Knowledge Base to a `MkDocs` project
- Converts Zammad source HTML to Markdown
- Converts multilanguage Knowledge Base to multilanguage MkDocs
- Downloads referenced images and adjusts the image links
- Grabs the Zammad Knowledge Base categories and converts them to MkDocs tags

## Requirements

- Zammad database must be available as a SQLite3 database file

## Usage

**🔥 This is work in progress - no liability for nothing.**

### Install

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install 'zammadkb2mkdocs @ git+https://github.com/tombreit/zammadkb2mkdocs'
```

### Run

```bash
zammadkb2mkdocs path/to/zammad-sqlite-dbfile --zammad-fqdn zammad.example.org
```

### Result

The Zammad Knowledge Base articles converted to Markdown files end up in `./dist/docs`.
Some other intermediate files such as the JSON representation of the Zammad Knowledge Base are also stored in `./dist`.

For your convenience, `mkdocs` will be installed with this package and you can view your new MkDocs knowledgebase base right now:

```bash
mkdocs serve
```

## Notes

- Currently only used/tested with a Zammad Knowledge Base in EN and DE.
- If the given `zammad-fqdn` is not reachable image src attributes will not be fixed and no images will be downloaded.
- To start from scratch: delete the automatically populated `./dist` directory.
