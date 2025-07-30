Installation
============

Requirements
------------

* Python 3.12 or higher
* pip package manager

Install from PyPI
-----------------

The easiest way to install lcvtoolbox is from PyPI:

.. code-block:: bash

   pip install lcvtoolbox

Install from Source
-------------------

To install the latest development version from source:

.. code-block:: bash

   git clone https://github.com/logiroad/cv-toolbox.git
   cd cv-toolbox
   pip install -e .

Development Installation
------------------------

For development, install with extra dependencies:

.. code-block:: bash

   git clone https://github.com/logiroad/cv-toolbox.git
   cd cv-toolbox
   pip install -e ".[dev,docs]"

This will install additional packages for:

* Testing (pytest, pytest-cov)
* Code quality (ruff, mypy, pre-commit)
* Documentation (sphinx, sphinx-rtd-theme)

Verify Installation
-------------------

To verify your installation:

.. code-block:: python

   import lcvtoolbox
   print(lcvtoolbox.__version__)

Or from the command line:

.. code-block:: bash

   cv-toolbox --help

Dependencies
------------

Core dependencies include:

* numpy: Numerical computing
* opencv-python: Computer vision operations
* Pillow: Image processing
* pydantic: Data validation
* matplotlib: Visualization
* requests: HTTP requests
* huggingface-hub: HuggingFace integration

All dependencies are automatically installed with the package.
