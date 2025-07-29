"""
Utility function for downloading datasets from Hugging Face Hub.
"""
import logging
from pathlib import Path
from typing import Optional
from datasets import IterableDataset, IterableDatasetDict, load_dataset


logger = logging.getLogger(__name__)


def download_dataset_from_hugging_face(
    dataset_name: str,
    local_path: Path,
    hf_token: Optional[str] = None,
    split: Optional[str] = None,
):
    """
    Download a dataset from Hugging Face Hub.

    Args:
        dataset_name (str): Name of the dataset on Hugging Face
        local_path (Path): Path where to save the dataset locally
        hf_token (Optional[str]): Hugging Face token for private datasets
        split (Optional[str]): Specific split to download (e.g., "train", "test")

    Returns:
        Dataset or DatasetDict: The downloaded dataset
    """
    

    logger.info(f"📥 Downloading dataset {dataset_name} to {local_path}")

    # Create the local directory if it doesn't exist
    local_path.mkdir(parents=True, exist_ok=True)

    # Download the dataset
    if split:
        dataset = load_dataset(dataset_name, split=split, token=hf_token)
    else:
        dataset = load_dataset(dataset_name, token=hf_token)

    # Save locally if the dataset supports it
    if hasattr(dataset, "save_to_disk") and not isinstance(dataset, (IterableDataset, IterableDatasetDict)):
        dataset.save_to_disk(str(local_path))
        logger.info(f"✅ Dataset downloaded and saved to {local_path}")
    else:
        logger.warning("⚠️ Dataset is streamed/iterable and cannot be saved to disk directly")

    return dataset
