# langchain-pptx2markdown

Community-maintained LangChain document loader for deterministic, structure-aware
PowerPoint parsing with [pptx2markdown](https://github.com/PPTX2Markdown/PPTX2Markdown).

This package is an independent community integration. It is not maintained or
endorsed by the LangChain team.

## Installation

```bash
pip install langchain-pptx2markdown
```

Python 3.10 through 3.14 are supported. Version 0.1 supports local `.pptx` files;
legacy `.ppt`, URLs, byte streams, and built-in chunking are intentionally out of scope.

The package must not be published until the Python 3.10/3.11 OMML backend release
gate in [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md) is resolved. The core parser's
temporary readable-text fallback is for compatibility testing, not the final
formula-support claim.

## Usage

```python
from langchain_pptx2markdown import PPTX2MarkdownLoader

loader = PPTX2MarkdownLoader("deck.pptx")
documents = loader.load()

for document in loader.lazy_load():
    print(document.metadata["slide_number"], document.page_content[:80])
```

Each non-empty slide becomes one `Document`. Hidden slides and speaker notes are
included by default. Slide numbers are 1-based and stored in metadata.

### Options

```python
loader = PPTX2MarkdownLoader(
    "deck.pptx",
    include_hidden=True,
    include_notes=True,
    include_empty=False,
    assets="omit",
    headings="auto",
    placeholder_inheritance="style",
    inherited_shapes="visible",
)
```

The default `assets="omit"` mode never returns links to temporary files. To retain
images and attachments, provide a durable directory:

```python
loader = PPTX2MarkdownLoader(
    "deck.pptx",
    assets="copy",
    asset_dir="./pptx-assets",
)
documents = loader.load()
```

Generated links use absolute `file:` URIs below
`./pptx-assets/<presentation-name>/`.

## Metadata

Every document includes `source`, `file_name`, `mime_type`, `slide_number`,
`hidden`, `schema_version`, and `content_types`.

## Development

```bash
python -m pip install -e ".[test]"
python -m unittest discover -v
ruff check src tests benchmarks
mypy src
python -m build
python -m twine check dist/*
```

See [CONTRIBUTING.md](CONTRIBUTING.md) and [SECURITY.md](SECURITY.md).
