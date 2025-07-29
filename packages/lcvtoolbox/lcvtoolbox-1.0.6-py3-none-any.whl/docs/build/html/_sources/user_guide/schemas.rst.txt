Schemas Guide
=============

The lcvtoolbox uses Pydantic models and TypedDict definitions to ensure data consistency and type safety throughout the project. All schemas are centralized in ``lcvtoolbox.core.schemas``.

GPS and Location Schemas
------------------------

GPS Coordinates
~~~~~~~~~~~~~~~

The ``GPSCoordinates`` schema represents geographical coordinates:

.. code-block:: python

   from lcvtoolbox.core.schemas import GPSCoordinates

   # Create GPS coordinates
   coords = GPSCoordinates(
       latitude=48.8566,
       longitude=2.3522,
       altitude=35.0  # Optional
   )

   # Convert to dictionary
   data = coords.model_dump()

GPS Point
~~~~~~~~~

The ``GPSPoint`` schema extends coordinates with additional metadata:

.. code-block:: python

   from lcvtoolbox.core.schemas import GPSPoint

   point = GPSPoint(
       latitude=48.8566,
       longitude=2.3522,
       timestamp=1234567890.123,
       accuracy=5.0,
       heading=180.0
   )

Camera Schemas
--------------

Camera Matrix
~~~~~~~~~~~~~

The ``CameraMatrixSchema`` represents camera intrinsic parameters:

.. code-block:: python

   from lcvtoolbox.core.schemas import CameraMatrixSchema

   camera = CameraMatrixSchema(
       fx=1435.0,  # Focal length in x
       fy=1435.0,  # Focal length in y
       cx=960.0,   # Principal point x
       cy=540.0    # Principal point y
   )

   # Convert to numpy matrix
   K = camera.to_matrix()

Camera Distortion
~~~~~~~~~~~~~~~~~

The ``CameraDistortionSchema`` handles lens distortion parameters:

.. code-block:: python

   from lcvtoolbox.core.schemas import CameraDistortionSchema

   distortion = CameraDistortionSchema(
       k1=-0.2,    # Radial distortion
       k2=0.1,
       p1=0.001,   # Tangential distortion
       p2=-0.001,
       k3=0.05     # Higher order radial
   )

Frame and Metadata Schemas
--------------------------

Frame Metadata
~~~~~~~~~~~~~~

The ``FrameMetadata`` schema stores comprehensive frame information:

.. code-block:: python

   from lcvtoolbox.core.schemas import FrameMetadata, GPSCoordinates

   frame = FrameMetadata(
       frame_id="frame_001",
       timestamp=1234567890.123,
       camera_id="camera_01",
       gps=GPSCoordinates(latitude=48.8566, longitude=2.3522),
       heading=180.0,
       speed=50.0,
       metadata={
           "weather": "sunny",
           "road_type": "highway"
       }
   )

Image Metadata
~~~~~~~~~~~~~~

For image-specific metadata:

.. code-block:: python

   from lcvtoolbox.core.schemas import ImageMetadata

   image_meta = ImageMetadata(
       filename="image_001.jpg",
       width=1920,
       height=1080,
       format="JPEG",
       timestamp=1234567890.123,
       camera_id="camera_01"
   )

Pose and Spatial Schemas
------------------------

Pose with RPY
~~~~~~~~~~~~~

The ``PoseRPYSchema`` represents 3D pose with Roll-Pitch-Yaw orientation:

.. code-block:: python

   from lcvtoolbox.core.schemas import PoseRPYSchema

   pose = PoseRPYSchema(
       x=10.0,
       y=20.0,
       z=5.0,
       roll=0.0,    # Degrees
       pitch=15.0,
       yaw=90.0
   )

   # Convert to transformation matrix
   T = pose.to_transformation_matrix()

UTM and Projection Schemas
--------------------------

UTM Reference
~~~~~~~~~~~~~

For working with UTM projections:

.. code-block:: python

   from lcvtoolbox.core.schemas import UTMReference

   utm_ref = UTMReference(
       zone=31,
       northern=True,
       epsg=32631
   )

Mask Projection Parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~

For projecting masks onto road surfaces:

.. code-block:: python

   from lcvtoolbox.core.schemas import MaskProjectionParams

   params = MaskProjectionParams(
       camera_height=4.5,
       camera_pitch=-10.0,
       road_width=12.0,
       projection_distance=50.0
   )

CVAT Schemas
------------

The package includes comprehensive schemas for CVAT integration:

Pydantic Models
~~~~~~~~~~~~~~~

.. code-block:: python

   from lcvtoolbox.core.schemas import (
       CvatApiTaskDetails,
       CvatApiJobDetails,
       CvatApiAttribute
   )

   # Task details from CVAT API
   task = CvatApiTaskDetails(
       id=1,
       name="Road Signs",
       status="completed",
       size=100,
       mode="annotation"
   )

TypedDict Definitions
~~~~~~~~~~~~~~~~~~~~~

For cases where TypedDict is preferred:

.. code-block:: python

   from lcvtoolbox.core.schemas import CvatApiTaskDict

   task_data: CvatApiTaskDict = {
       "id": 1,
       "name": "Road Signs",
       "status": "completed"
   }

Best Practices
--------------

1. **Always use schemas for data validation**:
   
   .. code-block:: python

      # Good
      coords = GPSCoordinates(latitude=lat, longitude=lon)
      
      # Avoid
      coords = {"latitude": lat, "longitude": lon}

2. **Leverage Pydantic's validation**:
   
   .. code-block:: python

      try:
          coords = GPSCoordinates(latitude=91.0, longitude=180.0)
      except ValidationError as e:
          print(f"Invalid coordinates: {e}")

3. **Use model_dump() for serialization**:
   
   .. code-block:: python

      # Convert to dict
      data = schema.model_dump()
      
      # Convert to JSON
      json_str = schema.model_dump_json()

4. **Type hints for better IDE support**:
   
   .. code-block:: python

      def process_frame(frame: FrameMetadata) -> dict:
          """Process frame with type safety."""
          return frame.model_dump()
