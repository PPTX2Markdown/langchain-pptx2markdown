# Release and LangChain listing checklist

## Blocking gates

- [ ] `pptx2markdown>=0.2.0` is published to PyPI.
- [ ] The OMML backend imports and converts formulas on Python 3.10 and 3.11.
  `omml2latex` 0.1.0 and 0.1.1 currently fail to import because `_parser.py:1148`
  places a backslash-containing string literal inside an f-string expression.
- [ ] The upstream fix below is released, or an Apache-2.0-compatible fork with
  attribution is published and used by the core parser.
- [ ] All operating-system/Python CI jobs and dependency-bound jobs pass.
- [ ] PyPI Trusted Publishing is configured for this repository.

Suggested upstream change:

```diff
-    return f"{acc_map.get(chr_val, '\\hat')}{{{e}}}"
+    accent = acc_map.get(chr_val, "\\hat")
+    return f"{accent}{{{e}}}"
```

## Package publication

- [ ] Confirm `langchain-pptx2markdown` is available on PyPI.
- [ ] Build wheel and sdist in a clean checkout and run `twine check`.
- [ ] Install the wheel on Python 3.10–3.14 and run the README examples.
- [ ] Publish 0.1.0 with Trusted Publishing and verify the PyPI project links.
- [ ] Tag the release and update the changelog.

## LangChain documentation

- [ ] Post `docs/langchain-proposal.md` to the LangChain Forum or docs tracker.
- [ ] Confirm that new community loader pages are accepted and obtain the current
  template/path before opening a PR.
- [ ] Run all benchmark providers on one machine with pinned versions and publish
  the raw JSON plus corpus notices.
- [ ] Update `docs/pptx2markdown.mdx` to the maintainer-provided template.
- [ ] Submit a documentation-only PR; do not submit integration code to LangChain
  or the archived `langchain-community` repository.
