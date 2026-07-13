"""PowerPoint document loader backed by pptx2markdown."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Literal

from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document
from pptx2markdown import parse
from pptx2markdown.main_converter.converter_models import SlideDocument

AssetMode = Literal["omit", "copy"]
MIME_TYPE = "application/vnd.openxmlformats-officedocument.presentationml.presentation"


def _render_slide(slide: SlideDocument, *, include_notes: bool) -> str:
    parts: list[str] = []
    for block in slide.blocks:
        content = block.content.strip()
        if not content:
            continue
        if block.kind == "heading" and block.heading_level is not None:
            content = f"{'#' * block.heading_level} {content}"
        parts.append(content)
    if include_notes and slide.notes and slide.notes.strip():
        parts.extend(["Speaker notes:", slide.notes.strip()])
    return "\n\n".join(parts).strip()


class PPTX2MarkdownLoader(BaseLoader):
    """Load a local PPTX as one LangChain ``Document`` per non-empty slide."""

    def __init__(
        self,
        file_path: str | Path,
        *,
        include_hidden: bool = True,
        include_notes: bool = True,
        include_empty: bool = False,
        assets: AssetMode = "omit",
        asset_dir: str | Path | None = None,
        headings: str = "auto",
        placeholder_inheritance: str = "style",
        inherited_shapes: str = "visible",
    ) -> None:
        self.file_path = Path(file_path).expanduser()
        self.include_hidden = include_hidden
        self.include_notes = include_notes
        self.include_empty = include_empty
        self.assets = assets
        self.asset_dir = Path(asset_dir).expanduser() if asset_dir is not None else None
        self.headings = headings
        self.placeholder_inheritance = placeholder_inheritance
        self.inherited_shapes = inherited_shapes

    def lazy_load(self) -> Iterator[Document]:
        """Parse the presentation and yield slides in presentation order."""

        source = self.file_path.resolve()
        presentation = parse(
            source,
            assets=self.assets,
            asset_dir=self.asset_dir,
            headings=self.headings,
            placeholder_inheritance=self.placeholder_inheritance,
            inherited_shapes=self.inherited_shapes,
        )
        for slide in presentation.slides:
            if slide.hidden and not self.include_hidden:
                continue
            page_content = _render_slide(slide, include_notes=self.include_notes)
            if not page_content and not self.include_empty:
                continue
            content_types = list(dict.fromkeys(block.kind for block in slide.blocks))
            yield Document(
                page_content=page_content,
                metadata={
                    "source": str(source),
                    "file_name": presentation.source.name,
                    "mime_type": MIME_TYPE,
                    "slide_number": slide.page,
                    "hidden": slide.hidden,
                    "schema_version": presentation.schema_version,
                    "content_types": content_types,
                },
            )
