"""
Utility function for pushing dictionaries to Hugging Face Hub as datasets.
"""
import json
import tempfile
import logging
from pathlib import Path
from typing import Dict, Optional
from datasets import Dataset
from datasets import Image as HFImage
from huggingface_hub import HfApi


logger = logging.getLogger(__name__)


def push_dict_to_hugging_face_dataset(
    data_dict: Dict,
    dataset_name: str,
    hf_token: str,
    id2label: Optional[Dict[int, str]] = None,
    private: bool = True,
    commit_message: str = "Update dataset",
) -> None:
    """
    Push a dictionary to Hugging Face Hub as a dataset with specific column handling.

    Args:
        data_dict (Dict): Dictionary containing the dataset data with the following possible keys:
            - image: List of local paths to images (required)
            - label: List of local paths to semantic masks (optional)
            - annotation: List of local paths to panoptic masks (optional)
            - objects: List of nested annotation dicts (stored as-is)
        dataset_name (str): Name of the dataset on Hugging Face (e.g., "username/dataset-name")
        hf_token (str): Hugging Face authentication token
        id2label (Optional[Dict[int, str]]): Mapping from class IDs to labels. Will be inverted and
            added as semantic_class_to_id column, and stored as id2label.json
        private (bool): Whether the dataset should be private (default: True)
        commit_message (str): Commit message for the push (default: "Update dataset")

    Example:
        data_dict = {
            "image": ["/path/to/img1.jpg", "/path/to/img2.jpg"],
            "label": ["/path/to/mask1.png", "/path/to/mask2.png"],
            "objects": [[{"bbox": [10, 20, 30, 40], "class": "car"}], [{"bbox": [50, 60, 70, 80], "class": "person"}]],
        }
        id2label = {0: "background", 1: "car", 2: "person"}
    """
    # Validate required fields
    if "image" not in data_dict:
        raise ValueError("'image' field is required in the data dictionary")

    # Get the number of examples from the image list
    num_examples = len(data_dict["image"])

    # Validate all lists have the same length
    for key, value in data_dict.items():
        if isinstance(value, list) and len(value) != num_examples:
            raise ValueError(
                f"Field '{key}' has {len(value)} items, but 'image' has {num_examples} items. All lists must have the same length."
            )

    logger.info(f"📦 Preparing to push dataset with {num_examples} examples to {dataset_name}")

    # Build the dataset dict for Hugging Face
    hf_data_dict = {}

    # Handle image column (convert paths to images)
    image_paths = data_dict["image"]
    # Validate that all image files exist
    for img_path in image_paths:
        if not Path(img_path).exists():
            raise ValueError(f"Image file not found: {img_path}")
    hf_data_dict["image"] = image_paths

    # Handle optional label column (semantic masks)
    if "label" in data_dict:
        label_paths = data_dict["label"]
        # Validate that all label files exist
        for label_path in label_paths:
            if not Path(label_path).exists():
                raise ValueError(f"Label file not found: {label_path}")
        hf_data_dict["label"] = label_paths
        logger.info("✅ Including 'label' column (semantic masks)")

    # Handle optional annotation column (panoptic masks)
    if "annotation" in data_dict:
        annotation_paths = data_dict["annotation"]
        # Validate that all annotation files exist
        for ann_path in annotation_paths:
            if not Path(ann_path).exists():
                raise ValueError(f"Annotation file not found: {ann_path}")
        hf_data_dict["annotation"] = annotation_paths
        logger.info("✅ Including 'annotation' column (panoptic masks)")

    # Handle objects column (store as-is)
    if "objects" in data_dict:
        hf_data_dict["objects"] = data_dict["objects"]
        logger.info("✅ Including 'objects' column")

    # Handle id2label -> semantic_class_to_id conversion
    if id2label is not None:
        # Invert id2label to create semantic_class_to_id
        semantic_class_to_id = {label: id_ for id_, label in id2label.items()}
        # Repeat the dict for each example
        hf_data_dict["semantic_class_to_id"] = [semantic_class_to_id] * num_examples
        logger.info("✅ Including 'semantic_class_to_id' column (inverted from id2label)")

    # Create the Dataset
    dataset = Dataset.from_dict(hf_data_dict)

    # Cast image columns to HF Image type
    dataset = dataset.cast_column("image", HFImage())

    if "label" in hf_data_dict:
        dataset = dataset.cast_column("label", HFImage())

    if "annotation" in hf_data_dict:
        dataset = dataset.cast_column("annotation", HFImage())

    # Initialize the Hugging Face API
    api = HfApi(token=hf_token)

    # Create the dataset repository if it doesn't exist
    try:
        api.create_repo(
            repo_id=dataset_name,
            repo_type="dataset",
            private=private,
            exist_ok=True,
            token=hf_token,
        )
        logger.info(f"📝 Dataset repository {dataset_name} created/verified")
    except Exception as e:
        logger.warning(f"⚠️ Could not create repository: {e}")

    # Push to Hugging Face Hub
    try:
        logger.info(f"🚀 Pushing dataset to {dataset_name}...")

        # Push the dataset
        dataset.push_to_hub(
            dataset_name,
            token=hf_token,
            private=private,
            commit_message=commit_message,
        )

        # If id2label is provided, also upload it as a separate JSON file
        if id2label is not None:
            

            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                # Save id2label.json
                id2label_file = temp_path / "id2label.json"
                with open(id2label_file, "w") as f:
                    json.dump(id2label, f, indent=2)

                api.upload_file(
                    path_or_fileobj=str(id2label_file),
                    path_in_repo="id2label.json",
                    repo_id=dataset_name,
                    repo_type="dataset",
                    token=hf_token,
                    commit_message="Add id2label mapping",
                )
                logger.info("✅ Uploaded id2label.json")

        logger.info(f"✅ Successfully pushed dataset to {dataset_name}")
        logger.info(f"🔗 View dataset at: https://huggingface.co/datasets/{dataset_name}")
    except Exception as e:
        logger.error(f"❌ Failed to push dataset to Hugging Face: {e}")
        raise
