"""
Utility function for pushing image classification datasets to Hugging Face Hub.
"""
import logging
from pathlib import Path
from typing import Dict, List
from datasets import Dataset, DatasetDict
from datasets import Image as HFImage
from huggingface_hub import HfApi


logger = logging.getLogger(__name__)


def push_image_classification_folders(
    dataset_name: str,
    local_dataset_path: Path,
    hf_token: str,
    private: bool = True,
    commit_message: str = "Update dataset",
) -> None:
    """
    Push a local image classification dataset to Hugging Face Hub.

    Args:
        dataset_name (str): Name of the dataset on Hugging Face (e.g., "username/dataset-name")
        local_dataset_path (Path): Path to the local dataset directory
        hf_token (str): Hugging Face authentication token
        private (bool): Whether the dataset should be private (default: True)
        commit_message (str): Commit message for the push (default: "Update dataset")

    The local dataset should follow this structure:
        local_dataset_path/
            ├── to_review/
            │   ├── train/
            │   │   ├── label1/
            │   │   │   ├── image1.png
            │   │   │   └── image2.png
            │   │   └── label2/
            │   │       └── image3.png
            │   └── test/
            │       └── label1/
            │           └── image4.png
            └── ...
    """
    if not local_dataset_path.exists():
        raise ValueError(f"Dataset path {local_dataset_path} does not exist")

    logger.info(f"📦 Preparing to push dataset from {local_dataset_path} to {dataset_name}")

    # Initialize the Hugging Face API
    api = HfApi(token=hf_token)

    # Prepare the dataset dictionary to hold all splits
    dataset_dict = {}

    # Look for the "to_review" directory (based on the fissures.py structure)
    to_review_path = local_dataset_path / "to_review"

    if not to_review_path.exists():
        logger.warning(f"⚠️ No 'to_review' directory found in {local_dataset_path}")
        return

    # Process each split (train, test, validation, etc.)
    for split_dir in to_review_path.iterdir():
        if not split_dir.is_dir():
            continue

        split_name = split_dir.name
        logger.info(f"📂 Processing split: {split_name}")

        # Collect all images and labels for this split
        image_paths: List[str] = []
        labels: List[str] = []

        # Iterate through label directories
        for label_dir in split_dir.iterdir():
            if not label_dir.is_dir():
                continue

            label_name = label_dir.name

            # Collect all images in this label directory
            for image_file in label_dir.glob("*.png"):
                image_paths.append(str(image_file))
                labels.append(label_name)

        if not image_paths:
            logger.warning(f"⚠️ No images found for split {split_name}")
            continue

        logger.info(f"📊 Found {len(image_paths)} images in {split_name} split")

        # Create a dataset for this split
        data_dict = {
            "image": image_paths,
            "label": labels,
        }

        # Create the Dataset object
        dataset = Dataset.from_dict(data_dict)

        # Cast the image column to the Hugging Face Image type
        dataset = dataset.cast_column("image", HFImage())

        # Add to the dataset dictionary
        dataset_dict[split_name] = dataset

    if not dataset_dict:
        logger.error("❌ No data found to push to Hugging Face")
        return

    # Create a DatasetDict from all splits
    dataset = DatasetDict(dataset_dict)

    # Log dataset information
    logger.info("📊 Dataset summary:")
    for split_name, split_dataset in dataset.items():
        logger.info(f"   - {split_name}: {len(split_dataset)} examples")

        # Count examples per label
        if "label" in split_dataset.column_names:
            label_counts: Dict[str, int] = {}
            for label in split_dataset["label"]:
                label_counts[label] = label_counts.get(label, 0) + 1
            for label, count in sorted(label_counts.items()):
                logger.info(f"     * {label}: {count} examples")

    # Push to Hugging Face Hub
    try:
        logger.info(f"🚀 Pushing dataset to {dataset_name}...")
        dataset.push_to_hub(
            dataset_name,
            token=hf_token,
            private=private,
            commit_message=commit_message,
        )
        logger.info(f"✅ Successfully pushed dataset to {dataset_name}")
    except Exception as e:
        logger.error(f"❌ Failed to push dataset to Hugging Face: {e}")
        raise
