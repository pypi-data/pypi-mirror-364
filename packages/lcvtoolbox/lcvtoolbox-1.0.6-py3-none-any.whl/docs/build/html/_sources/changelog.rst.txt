Changelog
=========

All notable changes to lcvtoolbox will be documented in this file.

The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_,
and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

[1.0.5] - 2025-01-23
--------------------

Added
~~~~~
- Comprehensive Sphinx documentation with automatic API generation
- Missing dependencies in pyproject.toml (matplotlib, requests, rich, huggingface-hub)
- Custom CSS for documentation styling

Changed
~~~~~~~
- Centralized all Pydantic and TypedDict schemas to `lcvtoolbox.core.schemas`
- Reorganized project structure for better maintainability
- Updated all imports to use the new centralized schema location

Fixed
~~~~~
- Circular import issues in pose.py module
- Missing exports in vision.encoding module
- Empty directories cleanup

[1.0.4] - Previous Release
--------------------------

Added
~~~~~
- Initial public release of lcvtoolbox
- Core functionality for computer vision tasks
- Integration with CVAT and HuggingFace
- CLI interface

See the full changelog in the `CHANGELOG.md <https://github.com/logiroad/cv-toolbox/blob/main/CHANGELOG.md>`_ file.
