Integrations Guide
==================

The lcvtoolbox provides seamless integration with popular computer vision platforms and services.

CVAT Integration
----------------

The CVAT integration allows you to interact with CVAT annotation platform programmatically.

API Client Setup
~~~~~~~~~~~~~~~~

.. code-block:: python

   from lcvtoolbox.integrations.cvat.api import CvatApi

   # Initialize API client
   api = CvatApi(
       host="http://localhost:8080",
       username="admin",
       password="admin"
   )

Working with Tasks
~~~~~~~~~~~~~~~~~~

Create and manage annotation tasks:

.. code-block:: python

   from lcvtoolbox.integrations.cvat.api import CvatTask

   # Create a new task
   task = CvatTask(
       api=api,
       name="Road Signs Detection",
       project_id=1,
       labels=[
           {"name": "stop_sign", "attributes": []},
           {"name": "speed_limit", "attributes": [
               {"name": "value", "type": "number"}
           ]}
       ]
   )

   # Upload images
   image_paths = ["img1.jpg", "img2.jpg", "img3.jpg"]
   task.upload_images(image_paths)

   # Check status
   status = task.get_status()
   print(f"Task status: {status}")

Managing Jobs
~~~~~~~~~~~~~

Work with annotation jobs:

.. code-block:: python

   from lcvtoolbox.integrations.cvat.api import CvatJob

   # Get all jobs for a task
   jobs = api.get_task_jobs(task_id=1)

   for job_data in jobs:
       job = CvatJob(api=api, job_id=job_data['id'])
       
       # Get annotations
       annotations = job.get_annotations()
       
       # Update annotations
       job.update_annotations(new_annotations)

Downloading Results
~~~~~~~~~~~~~~~~~~~

Export annotations in various formats:

.. code-block:: python

   # Download as COCO format
   task.download_annotations(
       output_path="annotations.json",
       format="COCO 1.0"
   )

   # Download as YOLO format
   task.download_annotations(
       output_path="annotations.zip",
       format="YOLO 1.1"
   )

HuggingFace Integration
-----------------------

The HuggingFace integration facilitates dataset management and model deployment.

Dataset Upload
~~~~~~~~~~~~~~

Push image classification datasets:

.. code-block:: python

   from lcvtoolbox.integrations.huggingface import push_image_classification_folders

   # Push dataset with folder structure
   push_image_classification_folders(
       dataset_name="username/my-dataset",
       data_dir="path/to/images",
       hf_token="your_token_here",
       private=True
   )

Dataset Synchronization
~~~~~~~~~~~~~~~~~~~~~~~

Sync datasets with configurable strategies:

.. code-block:: python

   from lcvtoolbox.integrations.huggingface import (
       pull_dataset_with_strategy,
       SyncStrategy
   )

   # Pull dataset with sync strategy
   pull_dataset_with_strategy(
       dataset_name="username/my-dataset",
       local_path=Path("./data"),
       hf_token="your_token",
       sync_strategy=SyncStrategy.IF_CHANGED
   )

Push Strategies
~~~~~~~~~~~~~~~

Different strategies for pushing data:

.. code-block:: python

   from lcvtoolbox.integrations.huggingface import (
       push_dataset_with_retry,
       PushStrategy
   )

   # Push with retry logic
   push_dataset_with_retry(
       dataset_name="username/my-dataset",
       local_path=Path("./data"),
       hf_token="your_token",
       max_retries=5,
       commit_message="Update dataset with new images"
   )

Endpoint Client
~~~~~~~~~~~~~~~

Interact with HuggingFace inference endpoints:

.. code-block:: python

   from lcvtoolbox.integrations.huggingface.endpoint import EndpointClient
   from PIL import Image

   # Initialize client
   client = EndpointClient(
       api_url="https://your-endpoint.endpoints.huggingface.cloud",
       token="your_token"
   )

   # Call with image
   image = Image.open("test.jpg")
   result = client.call_with_pil_image(image, threshold=0.5)

Working with Masks
~~~~~~~~~~~~~~~~~~

Handle segmentation masks for HuggingFace:

.. code-block:: python

   from lcvtoolbox.integrations.huggingface import HuggingFaceMask
   import numpy as np

   # Create mask handler
   mask_handler = HuggingFaceMask()

   # Convert numpy mask to HF format
   mask = np.zeros((480, 640), dtype=np.uint8)
   mask[100:200, 150:250] = 1

   hf_mask = mask_handler.to_huggingface_format(mask)

   # Convert back
   numpy_mask = mask_handler.from_huggingface_format(hf_mask)

Best Practices
--------------

CVAT Integration
~~~~~~~~~~~~~~~~

1. **Authentication**:
   - Store credentials securely (environment variables)
   - Use API tokens when available
   - Implement retry logic for network issues

2. **Batch Operations**:
   - Upload images in batches
   - Use pagination for large datasets
   - Cache task/job information locally

3. **Error Handling**:
   
   .. code-block:: python

      try:
          task.upload_images(images)
      except CvatApiError as e:
          logger.error(f"Upload failed: {e}")
          # Implement retry or recovery logic

HuggingFace Integration
~~~~~~~~~~~~~~~~~~~~~~~

1. **Dataset Organization**:
   - Follow HuggingFace dataset structure conventions
   - Include dataset cards (README.md)
   - Version your datasets properly

2. **Sync Strategies**:
   - Use `NEVER` for stable datasets
   - Use `IF_CHANGED` for development
   - Use `ALWAYS` for critical updates

3. **Network Efficiency**:
   
   .. code-block:: python

      # Use appropriate chunk sizes
      push_dict_to_hugging_face_dataset(
          data_dict=large_data,
          dataset_name="username/dataset",
          chunk_size=1000,  # Process in chunks
          max_workers=4     # Parallel uploads
      )

4. **Token Management**:
   - Never hardcode tokens
   - Use HuggingFace CLI for authentication
   - Rotate tokens regularly

Integration Examples
--------------------

CVAT to HuggingFace Pipeline
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Complete pipeline from CVAT annotations to HuggingFace dataset:

.. code-block:: python

   # 1. Download from CVAT
   task = CvatTask(api=api, task_id=123)
   annotations = task.download_annotations(format="COCO 1.0")

   # 2. Process annotations
   dataset = process_coco_to_dataset(annotations)

   # 3. Push to HuggingFace
   push_dict_to_hugging_face_dataset(
       data_dict=dataset,
       dataset_name="org/cvat-processed",
       hf_token=token
   )

Automated Sync
~~~~~~~~~~~~~~

Set up automated synchronization:

.. code-block:: python

   from pathlib import Path
   import schedule

   def sync_datasets():
       """Sync local and remote datasets."""
       datasets = ["dataset1", "dataset2", "dataset3"]
       
       for dataset in datasets:
           pull_dataset_with_strategy(
               dataset_name=f"org/{dataset}",
               local_path=Path(f"./data/{dataset}"),
               sync_strategy=SyncStrategy.IF_CHANGED
           )

   # Schedule hourly sync
   schedule.every().hour.do(sync_datasets)
