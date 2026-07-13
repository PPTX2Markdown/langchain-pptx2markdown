# Proposal: list `langchain-pptx2markdown` as a community document loader

`langchain-pptx2markdown` is an independently maintained LangChain loader for local
PowerPoint `.pptx` files. Before submitting a documentation PR, we would like to
confirm whether the current integrations documentation accepts new community
document loaders and which page template should be used.

The loader is backed by the MIT-licensed `pptx2markdown` parser and provides:

- native OOXML parsing without an ML model or hosted service;
- deterministic geometry-based reading order;
- slide/layout/master placeholder inheritance;
- native tables, charts, SmartArt, OMML formulas, speaker notes, and attachments;
- one LangChain `Document` per slide with stable 1-based source metadata;
- no temporary asset links in its default configuration;
- Python 3.10–3.14 and cross-platform CI.

The integration is published and maintained outside the LangChain repositories. Its
documentation will clearly identify it as an unverified community integration. We
will provide reproducible public-corpus benchmarks without claiming endorsement or
superiority over other loaders.

Proposed documentation path:
`src/oss/python/integrations/document_loaders/pptx2markdown.mdx`.
