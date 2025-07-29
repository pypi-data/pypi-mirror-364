Vision Guide
============

The vision module provides comprehensive tools for image processing, geometric computations, and camera operations.

Image Encoding
--------------

The encoding module offers flexible image compression options:

Basic Encoding
~~~~~~~~~~~~~~

.. code-block:: python

   from lcvtoolbox.vision.encoding import encode_image_to_string, decode_string_to_image
   from PIL import Image

   # Load image
   image = Image.open("photo.jpg")
   
   # Encode to base64 string
   encoded = encode_image_to_string(image, quality=90)
   
   # Decode back
   decoded = decode_string_to_image(encoded)

Compression Presets
~~~~~~~~~~~~~~~~~~~

Use predefined presets for common scenarios:

.. code-block:: python

   from lcvtoolbox.vision.encoding import encode_image_to_string, CompressionPreset

   # Lossless compression
   lossless = encode_image_to_string(image, preset=CompressionPreset.LOSSLESS_MAX)
   
   # Balanced quality/size
   balanced = encode_image_to_string(image, preset=CompressionPreset.BALANCED)
   
   # Minimize size
   tiny = encode_image_to_string(image, preset=CompressionPreset.TINY)

Adaptive Encoding
~~~~~~~~~~~~~~~~~

Automatically adjust quality to meet size constraints:

.. code-block:: python

   from lcvtoolbox.vision.encoding import encode_image_adaptive

   # Target 500KB file size
   encoded, quality = encode_image_adaptive(
       image,
       target_size_kb=500,
       min_quality=60,
       max_quality=95
   )
   print(f"Achieved quality: {quality}")

Mask Encoding
-------------

Efficient binary mask compression:

.. code-block:: python

   from lcvtoolbox.vision.encoding import (
       encode_mask_to_string,
       decode_mask_from_string,
       MaskFormat
   )
   import numpy as np

   # Create a binary mask
   mask = np.zeros((480, 640), dtype=np.uint8)
   mask[100:200, 150:250] = 255

   # Encode using COCO RLE format
   encoded = encode_mask_to_string(mask, format=MaskFormat.RLE_COCO)
   
   # Decode back
   decoded = decode_mask_from_string(encoded, (480, 640))

Batch Processing
~~~~~~~~~~~~~~~~

Process multiple masks efficiently:

.. code-block:: python

   from lcvtoolbox.vision.encoding import encode_mask_batch

   masks = [mask1, mask2, mask3, ...]
   
   # Parallel encoding
   encoded_masks = encode_mask_batch(
       masks,
       format=MaskFormat.RLE_COCO,
       parallel=True
   )

Camera Operations
-----------------

Camera Calibration
~~~~~~~~~~~~~~~~~~

Adjust camera parameters for different image sizes:

.. code-block:: python

   from lcvtoolbox.vision.camera import adjust_intrinsic_with_size
   import numpy as np

   # Original camera matrix
   K = np.array([
       [1435, 0, 960],
       [0, 1435, 540],
       [0, 0, 1]
   ])
   
   # Adjust for new size
   K_new = adjust_intrinsic_with_size(
       K,
       original_size=(1920, 1080),
       new_size=(1280, 720)
   )

Geometric Primitives
--------------------

3D Points
~~~~~~~~~

.. code-block:: python

   from lcvtoolbox.vision.geometry.primitives import Point3D

   # Create points
   p1 = Point3D(1, 2, 3)
   p2 = Point3D(4, 5, 6)
   
   # Operations
   distance = p1.distance_to(p2)
   midpoint = p1.midpoint(p2)
   
   # Vector operations
   v = p2 - p1  # Vector from p1 to p2
   scaled = p1 * 2.0

3D Transformations
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from lcvtoolbox.vision.geometry.primitives import (
       TransformationMatrix,
       PoseRPY,
       RPY
   )

   # Create pose
   position = Point3D(10, 20, 5)
   orientation = RPY.from_degrees(roll=0, pitch=15, yaw=90)
   pose = PoseRPY(position, orientation)
   
   # Convert to transformation matrix
   T = pose.to_transformation_matrix()
   
   # Apply transformation
   p_transformed = T.transform_point(p1)

Rotations
~~~~~~~~~

Multiple rotation representations:

.. code-block:: python

   from lcvtoolbox.vision.geometry.primitives import (
       RotationMatrix,
       Quaternion,
       RPY,
       AxisAngle
   )

   # Create rotation from RPY
   rpy = RPY.from_degrees(30, 45, 60)
   
   # Convert between representations
   R = rpy.to_rotation_matrix()
   q = rpy.to_quaternion()
   aa = rpy.to_axis_angle()
   
   # Apply rotation
   v_rotated = R.rotate_vector(v)

Image Processing
----------------

Tiling
~~~~~~

Split images into tiles for processing:

.. code-block:: python

   from lcvtoolbox.vision.image import tile_image, PaddingStrategy

   tiles = tile_image(
       image,
       tile_size=(512, 512),
       overlap=64,
       padding=PaddingStrategy.REFLECT
   )
   
   for tile, (x, y) in tiles:
       # Process each tile
       processed = process_tile(tile)

Cropping
~~~~~~~~

Intelligent cropping operations:

.. code-block:: python

   from lcvtoolbox.vision.image import Cropper

   cropper = Cropper(maintain_aspect=True)
   
   # Crop to specific size
   cropped = cropper.crop_center(image, (800, 600))
   
   # Smart crop based on content
   smart_crop = cropper.crop_smart(image, target_size=(800, 600))

Projection
----------

Road Surface Projection
~~~~~~~~~~~~~~~~~~~~~~~

Project image coordinates to road surface:

.. code-block:: python

   from lcvtoolbox.vision.geometry.projection import PlaneRoadModel

   # Setup road model
   road_model = PlaneRoadModel(
       camera_height=4.5,
       camera_pitch=-10.0,
       focal_length=1435.0
   )
   
   # Project image point to road
   image_point = (640, 480)
   road_point = road_model.project_to_road(image_point)

Best Practices
--------------

1. **Choose appropriate compression**:
   - Use lossless for analysis tasks
   - Use lossy for visualization/storage
   - Use adaptive for size constraints

2. **Batch process when possible**:
   - Use parallel encoding for multiple images/masks
   - Process tiles in parallel for large images

3. **Handle coordinate systems carefully**:
   - Document your coordinate conventions
   - Use transformation matrices for complex transforms
   - Validate geometric operations with unit tests

4. **Memory efficiency**:
   - Use generators for large datasets
   - Process images in tiles when needed
   - Clean up large arrays after use
