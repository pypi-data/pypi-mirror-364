Contributing
============

We welcome contributions to lcvtoolbox! This guide will help you get started.

Development Setup
-----------------

1. Fork the repository on GitHub
2. Clone your fork locally:

   .. code-block:: bash

      git clone https://github.com/YOUR_USERNAME/cv-toolbox.git
      cd cv-toolbox

3. Install in development mode:

   .. code-block:: bash

      pip install -e ".[dev,docs]"

4. Install pre-commit hooks:

   .. code-block:: bash

      pre-commit install

Code Style
----------

We use the following tools to maintain code quality:

* **ruff**: For linting and formatting
* **mypy**: For type checking
* **pytest**: For testing

Run all checks:

.. code-block:: bash

   make lint
   make test

Submitting Changes
------------------

1. Create a new branch for your feature:

   .. code-block:: bash

      git checkout -b feature/your-feature-name

2. Make your changes and commit them:

   .. code-block:: bash

      git add .
      git commit -m "Add your feature"

3. Push to your fork:

   .. code-block:: bash

      git push origin feature/your-feature-name

4. Open a pull request on GitHub

Documentation
-------------

When adding new features, please update the documentation:

1. Add docstrings to all public functions and classes
2. Update relevant documentation files
3. Build and test the documentation:

   .. code-block:: bash

      cd docs
      make html

Testing
-------

Write tests for new functionality:

.. code-block:: python

   def test_my_feature():
       """Test the new feature."""
       assert my_feature() == expected_result

Run tests with coverage:

.. code-block:: bash

   pytest --cov=lcvtoolbox

License
-------

By contributing, you agree that your contributions will be licensed under the project's license.
