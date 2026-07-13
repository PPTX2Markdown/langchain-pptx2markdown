from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from pptx2markdown.main_converter.converter_models import (
    ContentBlock,
    PresentationDocument,
    SlideDocument,
    SourceDocument,
)

from langchain_pptx2markdown import PPTX2MarkdownLoader


def _presentation() -> PresentationDocument:
    return PresentationDocument(
        source=SourceDocument(name="deck.pptx", format="pptx"),
        slides=[
            SlideDocument(
                page=1,
                blocks=[
                    ContentBlock(kind="heading", content="Title", heading_level=1),
                    ContentBlock(kind="text", content="Body"),
                ],
            ),
            SlideDocument(
                page=2,
                hidden=True,
                blocks=[ContentBlock(kind="table", content="| A |\n| - |")],
                notes="Explain the table.",
            ),
            SlideDocument(page=3),
        ],
    )


class LoaderTests(unittest.TestCase):
    @patch("langchain_pptx2markdown.loader.parse", return_value=_presentation())
    def test_load_and_lazy_load_return_slide_documents(self, mocked_parse) -> None:
        loader = PPTX2MarkdownLoader("deck.pptx")

        loaded = loader.load()
        lazy_loaded = list(loader.lazy_load())

        self.assertEqual(loaded, lazy_loaded)
        self.assertEqual([doc.metadata["slide_number"] for doc in loaded], [1, 2])
        self.assertEqual(loaded[0].page_content, "# Title\n\nBody")
        self.assertIn("Speaker notes:\n\nExplain the table.", loaded[1].page_content)
        self.assertTrue(loaded[1].metadata["hidden"])
        self.assertEqual(loaded[0].metadata["content_types"], ["heading", "text"])
        json.dumps([doc.metadata for doc in loaded])
        self.assertEqual(mocked_parse.call_count, 2)

    @patch("langchain_pptx2markdown.loader.parse", return_value=_presentation())
    def test_filters_are_explicit(self, _mocked_parse) -> None:
        loader = PPTX2MarkdownLoader(
            "deck.pptx",
            include_hidden=False,
            include_notes=False,
            include_empty=True,
        )

        documents = loader.load()

        self.assertEqual([doc.metadata["slide_number"] for doc in documents], [1, 3])
        self.assertEqual(documents[1].page_content, "")

    @patch("langchain_pptx2markdown.loader.parse", return_value=_presentation())
    def test_asset_options_are_forwarded(self, mocked_parse) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            asset_dir = Path(temporary)
            loader = PPTX2MarkdownLoader("deck.pptx", assets="copy", asset_dir=asset_dir)
            loader.load()

        kwargs = mocked_parse.call_args.kwargs
        self.assertEqual(kwargs["assets"], "copy")
        self.assertEqual(kwargs["asset_dir"], asset_dir)


if __name__ == "__main__":
    unittest.main()
