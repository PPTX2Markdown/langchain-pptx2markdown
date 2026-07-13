"""LangChain integration for pptx2markdown."""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _package_version

from langchain_pptx2markdown.loader import PPTX2MarkdownLoader

try:
    __version__ = _package_version("langchain-pptx2markdown")
except PackageNotFoundError:
    __version__ = "0.0.0"

__all__ = ["PPTX2MarkdownLoader", "__version__"]
