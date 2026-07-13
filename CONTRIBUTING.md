# Contributing

Open an issue before changing the public loader contract. Bug reports should include
the package versions, operating system, Python version, a minimal reproducible PPTX
when licensing permits, and the expected slide output.

Install the test extra, then run the commands in the README. New behavior requires
unit tests and, for parsing changes, a regression fixture in the core
`pptx2markdown` repository. Pull requests must keep runtime dependencies minimal and
must not introduce network access during document loading.
