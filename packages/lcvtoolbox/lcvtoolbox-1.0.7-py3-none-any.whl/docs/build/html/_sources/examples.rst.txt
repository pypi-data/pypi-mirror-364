Examples
========

This section provides practical examples of using lcvtoolbox in real-world scenarios.

Image Processing Pipeline
-------------------------

Here's a complete example of processing images with encoding and geometric transformations:

.. code-block:: python

   import numpy as np
   from PIL import Image
   from lcvtoolbox.vision.encoding import (
       encode_image_to_string, 
       decode_string_to_image,
       CompressionPreset
   )
   from lcvtoolbox.vision.geometry.primitives import Point3D, TransformationMatrix

   # Load and encode an image
   image = Image.open("input.jpg")
   
   # Encode with different quality presets
   high_quality = encode_image_to_string(image, preset=CompressionPreset.HIGH_QUALITY)
   balanced = encode_image_to_string(image, preset=CompressionPreset.BALANCED)
   small_size = encode_image_to_string(image, preset=CompressionPreset.SMALL_SIZE)
   
   print(f"High quality size: {len(high_quality)} bytes")
   print(f"Balanced size: {len(balanced)} bytes")
   print(f"Small size: {len(small_size)} bytes")

Working with Frame Metadata
---------------------------

Managing metadata for video frames or image sequences:

.. code-block:: python

   from lcvtoolbox.core.schemas import FrameMetadata, GPSCoordinates
   from lcvtoolbox.data.metadata.frames import FramesMetadata
   
   # Create frame metadata
   frame1 = FrameMetadata(
       frame_id="frame_001",
       timestamp=1234567890.123,
       gps=GPSCoordinates(latitude=48.8566, longitude=2.3522),
       camera_id="camera_01"
   )
   
   frame2 = FrameMetadata(
       frame_id="frame_002",
       timestamp=1234567891.123,
       gps=GPSCoordinates(latitude=48.8567, longitude=2.3523),
       camera_id="camera_01"
   )
   
   # Create a collection
   frames = FramesMetadata()
   frames.add_frame(frame1)
   frames.add_frame(frame2)
   
   # Save to JSON
   frames.save_to_json("frames_metadata.json")

Camera Calibration Example
--------------------------

Working with camera calibration data:

.. code-block:: python

   from lcvtoolbox.core.schemas import CameraMatrixSchema, CameraDistortionSchema
   from lcvtoolbox.vision.camera import adjust_intrinsic_with_size
   import numpy as np
   
   # Define camera parameters
   camera = CameraMatrixSchema(
       fx=1435.0,
       fy=1435.0,
       cx=960.0,
       cy=540.0
   )
   
   distortion = CameraDistortionSchema(
       k1=-0.2,
       k2=0.1,
       p1=0.001,
       p2=-0.001,
       k3=0.05
   )
   
   # Original image size
   original_size = (1920, 1080)
   new_size = (1280, 720)
   
   # Adjust intrinsics for new image size
   new_camera = adjust_intrinsic_with_size(
       camera.to_matrix(),
       original_size,
       new_size
   )
   
   print(f"Original camera matrix:\n{camera.to_matrix()}")
   print(f"Adjusted camera matrix:\n{new_camera}")

CVAT Integration Example
------------------------

Interacting with CVAT for annotation management:

.. code-block:: python

   from lcvtoolbox.integrations.cvat.api import CvatApi, CvatTask
   
   # Initialize API client
   api = CvatApi(
       host="http://localhost:8080",
       username="admin",
       password="admin"
   )
   
   # Create a new task
   task = CvatTask(
       api=api,
       name="Road Signs Detection",
       project_id=1
   )
   
   # Upload images
   image_paths = ["image1.jpg", "image2.jpg", "image3.jpg"]
   task.upload_images(image_paths)
   
   # Get task status
   status = task.get_status()
   print(f"Task status: {status}")

Batch Processing with Masks
---------------------------

Processing multiple masks efficiently:

.. code-block:: python

   from lcvtoolbox.vision.encoding import (
       encode_mask_batch,
       MaskFormat
   )
   import numpy as np
   
   # Create sample masks
   masks = []
   for i in range(10):
       mask = np.zeros((480, 640), dtype=np.uint8)
       # Add some random shapes
       mask[100:200, 150:250] = 255
       mask[300:350, 400:500] = 255
       masks.append(mask)
   
   # Batch encode masks
   encoded_masks = encode_mask_batch(
       masks,
       format=MaskFormat.RLE_COCO,
       parallel=True
   )
   
   print(f"Encoded {len(encoded_masks)} masks")
   
   # Calculate compression ratio
   original_size = sum(m.nbytes for m in masks)
   encoded_size = sum(len(str(e)) for e in encoded_masks)
   ratio = original_size / encoded_size
   print(f"Compression ratio: {ratio:.2f}x")

For more examples, check out the project's GitHub repository.
