# Reproducible parser benchmark

The benchmark runs every selected parser against the same local public PPTX corpus
and the same checked-in `PresentationDocument` goldens. It reports parse success,
wall-clock duration, Python peak allocation, token recall, order similarity, and
per-content-kind recall. These metrics are evidence, not an endorsement or a claim
that one parser is universally better.

From a checkout of the core `PPTX2Markdown` repository:

```bash
python langchain-pptx2markdown/benchmarks/run_benchmark.py \
  --corpus tests/fixtures/golden \
  --goldens tests/fixtures/golden/expected/json \
  --providers pptx2markdown \
  --output langchain-pptx2markdown/benchmarks/results/pptx2markdown.json
```

To compare optional parsers, install pinned versions in a fresh environment and use
`--providers pptx2markdown,docling,unstructured`. Publish the generated environment
metadata, source corpus notices, exact command, and unedited result JSON. Do not
commit benchmark claims until all providers were run on the same machine and files.
