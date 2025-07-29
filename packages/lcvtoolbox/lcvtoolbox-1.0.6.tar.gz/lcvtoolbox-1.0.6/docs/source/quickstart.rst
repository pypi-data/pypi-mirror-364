Quick Start
===========

This guide will help you get started with lcvtoolbox quickly.

Basic Usage
-----------

Working with GPS Coordinates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from lcvtoolbox.core.schemas import GPSCoordinates

   # Create GPS coordinates
   coords = GPSCoordinates(latitude=48.8566, longitude=2.3522)
   print(f"Location: {coords}")

Image Encoding
~~~~~~~~~~~~~~

.. code-block:: python

   from lcvtoolbox.vision.encoding import encode_image_to_string, decode_string_to_image
   from PIL import Image

   # Encode an image to base64 string
   image = Image.open("photo.jpg")
   encoded = encode_image_to_string(image, quality=90)
   
   # Decode back to image
   decoded_image = decode_string_to_image(encoded)

Working with 3D Points
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from lcvtoolbox.vision.geometry.primitives import Point3D

   # Create 3D points
   p1 = Point3D(1, 2, 3)
   p2 = Point3D(4, 5, 6)
   
   # Calculate distance
   distance = p1.distance_to(p2)
   print(f"Distance: {distance:.2f}")
   
   # Find midpoint
   midpoint = p1.midpoint(p2)
   print(f"Midpoint: {midpoint}")

Camera Calibration
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from lcvtoolbox.core.schemas import CameraMatrixSchema
   import numpy as np

   # Define camera matrix
   camera = CameraMatrixSchema(
       fx=1000.0,
       fy=1000.0,
       cx=640.0,
       cy=480.0
   )
   
   # Convert to numpy array
   K = camera.to_matrix()
   print(f"Camera matrix:\n{K}")

Using the CLI
-------------

The package includes a command-line interface:

.. code-block:: bash

   # Show version
   cv-toolbox version

   # Demo spatial primitives
   cv-toolbox demo

   # Get help
   cv-toolbox --help

Integration Examples
--------------------

HuggingFace Integration
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from lcvtoolbox.integrations.huggingface import push_image_classification_folders

   # Push a dataset to HuggingFace
   push_image_classification_folders(
       dataset_name="my-org/my-dataset",
       data_dir="path/to/images",
       hf_token="your_token_here"
   )

CVAT Integration
~~~~~~~~~~~~~~~~

.. code-block:: python

   from lcvtoolbox.integrations.cvat.api import CvatApi

   # Initialize CVAT API client
   api = CvatApi(
       host="http://localhost:8080",
       username="admin",
       password="admin"
   )

Next Steps
----------

* Explore the :doc:`user_guide/schemas` for data validation
* Learn about :doc:`user_guide/vision` for image processing
* Check out :doc:`user_guide/integrations` for external services
* Read the :doc:`api/modules` for detailed API documentation
