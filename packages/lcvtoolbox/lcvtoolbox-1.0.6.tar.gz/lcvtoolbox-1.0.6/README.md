# CV Toolbox

Just another computer vision toolbox.

This project is not ready for public use.

If you look for comprehensive libraries consider these alternatives:

- [pytransform3d](https://pypi.org/project/pytransform3d/) for 3D computations
- [shapely](https://pypi.org/project/shapely/) for 2D computations
- [CVAT SDK](https://docs.cvat.ai/docs/api_sdk/sdk/) to interact with CVAT
- [Hub client library](https://huggingface.co/docs/huggingface_hub/index) to interact with Hugging Face

## Installation

### Only available on PyPI

```bash
# Install the latest version
pip install lcvtoolbox

# Install a specific version
pip install lcvtoolbox==1.0.1

# Install with optional dependencies
pip install lcvtoolbox[dev]  # Development tools
pip install lcvtoolbox[docs]  # Documentation tools
pip install lcvtoolbox[dev,docs]  # All optional dependencies
```

### System Requirements

- Python 3.12 or higher
- pip (Python package installer)

For OpenCV support, you may need system libraries:

```bash
# Ubuntu/Debian
sudo apt-get update && sudo apt-get install -y \
    libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1

# macOS
brew install opencv

# Windows: Should work out of the box
```

## Python API

```python
import lcvtoolbox

# Example usage of spatial primitives
from lcvtoolbox.spatial.primitives import Point

# Create a 3D point
point = Point(x=1.0, y=2.0, z=3.0)
```

## Features

### Spatial Primitives

- **Points and Vectors**: 3D point and vector operations
- **Rotations**: Support for multiple rotation representations (quaternion, Euler angles, rotation matrix, axis-angle)
- **Poses**: 6DOF pose representations with transformations
- **Coordinate Transformations**: Convert between different coordinate systems

### Computer Vision Tools

- **Image Processing**: Cropping, tiling, and preprocessing utilities
- **CVAT Integration**: API client for CVAT annotation platform
- **Hugging Face Integration**: Tools for dataset management

## License

All rights reserved.
