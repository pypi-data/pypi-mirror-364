# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.6] - 2025-07-18

Massive change, while not major version was created as the package is not yet in production.

### Changed

- Total re-organization of the folders structure

### Added

- Projection of masks in the world frame
- init files written for simpler imports
- Comprehensive test suite created
- Documentation created

## [1.0.5] - 2025-07-18

### Changed

- Debug placeholders

## [1.0.4] - 2025-07-18

### Added

- created placeholders

### Changed

- Moved first deployment consideration from DEPLOYMENT.md to FIRST_DEPLOY

## [1.0.3] - 2025-0-21

### Added

- Added placeholder directory with functions to create dummy images and masks.

## [1.0.2] - 2025-07-18

### Added

- PyPI deployment support
- Manual deployment documentation and scripts
- Version information in package __init__.py

### Changed

- Migrated from GitHub Packages to PyPI for package distribution
- Package renamed to `lcvtoolbox` for PyPI compatibility
- Module renamed from `cv_toolbox` to `lcvtoolbox`
- All imports updated to use new module name
- Updated installation instructions in all documentation
- Simplified package installation process for end users
- Manual deployment process (no automated CI/CD)

### Removed

- GitHub Packages deployment configuration
- GitHub Actions workflows

### Fixed

- Import paths throughout the codebase
- Package naming conflicts with PyPI

## [1.0.1] - 2025-01-18

### Added

- Initial release with core functionality
- Spatial primitives module with 3D transformations
- CVAT API integration
- Image processing utilities (cropping, tiling)
- Command-line interface
- Comprehensive test suite

### Features

- __Spatial Primitives__: Point, Vector, Quaternion, Euler angles, Rotation matrices
- __Pose Representations__: 6DOF poses with various rotation formats
- __CVAT Integration__: API client for annotation management
- __Image Tools__: Cropping and tiling utilities
- __CLI__: Unified command-line interface

[1.0.2]: https://github.com/logiroad/cv-toolbox/compare/v1.0.1...v1.0.2
[1.0.1]: https://github.com/logiroad/cv-toolbox/releases/tag/v1.0.1
