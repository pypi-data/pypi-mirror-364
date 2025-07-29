"""Handle Hugging Face classification dataset creation."""

import logging
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from datasets import (
    ClassLabel,
    Dataset,
    DatasetDict,
    Features,
    IterableDataset,
    IterableDatasetDict,
    concatenate_datasets,
    load_dataset,
)
from datasets import Image as HFImage
from huggingface_hub import HfApi, create_repo, repo_exists
from PIL import Image

logger = logging.getLogger(__name__)


class ImageClassificationDatasetProcessor:
    """
    Processor for creating a Hugging Face classification dataset.
    - Create an empty dataset with the specified classes on huggingface.co if needed.
    - Add each image to the dataset with its corresponding label.

    A classification datasets as splits (train/validation/test) and labels.

    There are two columns:
    - `image`: The image file.
    - `label`: The label for the image, which is one of the classification labels.

    """

    def __init__(
        self,
        hf_token: str,
        classification_labels: List[str],
        dataset: str,
        use_memory_efficient: bool = True,
        batch_size: int = 1000,
    ):
        """
        Initialize the processor.

        :param hf_token: Hugging Face token for authentication
        :param classification_labels: List of classification labels
        :param dataset: Dataset name on HuggingFace (e.g., "Logiroad/fissures-classification")
        :param use_memory_efficient: If True, use memory-efficient incremental updates
        :param batch_size: Number of images to accumulate before pushing to hub
        """
        self.hf_token = hf_token
        self.classification_labels = classification_labels
        self.dataset = dataset
        self.api = HfApi(token=hf_token)
        self._dataset_dict: Optional[DatasetDict] = None
        self._features = None
        self.use_memory_efficient = use_memory_efficient
        self.batch_size = batch_size
        self._current_batch = {"train": [], "validation": [], "test": []}
        self._batch_counts = {"train": 0, "validation": 0, "test": 0}

    @property
    def labels(self) -> List[str]:
        """
        Get the classification labels.
        """
        return self.classification_labels

    @property
    def dataset_name(self) -> Optional[str]:
        """
        Get the dataset name on HuggingFace.
        Ex: Logiroad/fissures-classification
        """
        return self.dataset

    def initialize_dataset(self) -> None:
        """
        If needed, create an empty classification dataset on Hugging Face.
        Includes a train/validation/test split.
        It includes two columns:
        - `image`: The image file.
        - `label`: The label for the image, which is one of the classification labels.
        """
        if not self.dataset_name:
            raise ValueError("Dataset name is required but not provided in configuration")

        # Check if repository exists
        try:
            if not repo_exists(self.dataset_name, repo_type="dataset", token=self.hf_token):
                logger.info(f"Creating new dataset repository: {self.dataset_name}")
                create_repo(self.dataset_name, repo_type="dataset", private=True, token=self.hf_token)
            else:
                logger.info(f"Dataset repository already exists: {self.dataset_name}")
        except Exception as e:
            logger.error(f"Error checking/creating dataset repository: {e}")
            raise

        # Define features for the dataset
        self._features = Features({"image": HFImage(), "label": ClassLabel(names=self.labels)})

        # Create empty dataset with splits
        self._dataset_dict = DatasetDict(
            {
                "train": Dataset.from_dict({"image": [], "label": []}, features=self._features),
                "validation": Dataset.from_dict({"image": [], "label": []}, features=self._features),
                "test": Dataset.from_dict({"image": [], "label": []}, features=self._features),
            }
        )

        logger.info(f"Initialized empty dataset with labels: {self.labels}")

    def reset_dataset(self) -> None:
        """
        Reset the dataset by removing all images and labels.
        This is useful to start fresh without creating a new dataset.
        """
        logger.info(f"Resetting dataset '{self.dataset_name}'")

        # Define features if not already defined
        if self._features is None:
            self._features = Features({"image": HFImage(), "label": ClassLabel(names=self.labels)})

        # Create empty dataset with splits
        self._dataset_dict = DatasetDict(
            {
                "train": Dataset.from_dict({"image": [], "label": []}, features=self._features),
                "validation": Dataset.from_dict({"image": [], "label": []}, features=self._features),
                "test": Dataset.from_dict({"image": [], "label": []}, features=self._features),
            }
        )

        # Push empty dataset to hub
        try:
            self._dataset_dict.push_to_hub(
                self.dataset_name, token=self.hf_token, commit_message="Reset dataset - removed all data"
            )
            logger.info(f"Successfully reset dataset on Hugging Face: {self.dataset_name}")
        except Exception as e:
            logger.error(f"Error resetting dataset on Hugging Face: {e}")
            raise

    def add_image(self, image: Image.Image, label: str, split: str = "train") -> None:
        """
        Add an image to the dataset with its corresponding label.
        :param image: The image to add.
        :param label: The label for the image.
        :param split: The split to add the image to (train/validation/test).
        """
        self.add_images([image], [label], split)

    def add_images(
        self, images: List[Image.Image], labels: List[str], split: str = "train", force_push: bool = False
    ) -> None:
        """
        Add multiple images to the dataset with their corresponding labels.
        :param images: List of images to add.
        :param labels: List of labels for the images.
        :param split: The split to add the images to (train/validation/test).
        :param force_push: Force push current batch regardless of size (for memory-efficient mode).
        """
        if len(images) != len(labels):
            raise ValueError(f"Number of images ({len(images)}) must match number of labels ({len(labels)})")

        if split not in ["train", "validation", "test"]:
            raise ValueError(f"Split must be one of 'train', 'validation', or 'test', got '{split}'")

        # Validate all labels
        for label in labels:
            if label not in self.labels:
                raise ValueError(f"Label '{label}' not in allowed labels: {self.labels}")

        logger.info(f"Adding {len(images)} images to '{split}' split")

        # Use memory-efficient mode if enabled
        if self.use_memory_efficient:
            self._add_images_memory_efficient(images, labels, split, force_push)
            return

        # Load existing dataset from hub if not already loaded
        if self._dataset_dict is None:
            if not self.dataset_name:
                raise ValueError("Dataset name is required but not provided in configuration")

            try:
                loaded_dataset = load_dataset(self.dataset_name, token=self.hf_token)
                # Ensure we have a DatasetDict
                if isinstance(loaded_dataset, DatasetDict):
                    self._dataset_dict = loaded_dataset
                elif isinstance(loaded_dataset, Dataset):
                    # If it's a single Dataset, wrap it in a DatasetDict
                    self._dataset_dict = DatasetDict([(split, loaded_dataset)])
                else:
                    # For other types (IterableDataset, etc.), create a new dataset
                    raise ValueError(f"Unsupported dataset type: {type(loaded_dataset)}")
                logger.info(f"Loaded existing dataset from hub: {self.dataset_name}")
            except Exception as e:
                logger.warning(f"Could not load dataset from hub, initializing new one: {e}")
                self.initialize_dataset()

        # Create new data dict
        new_data = {"image": images, "label": labels}

        # Create dataset from new data
        if self._features is None:
            self._features = Features({"image": HFImage(), "label": ClassLabel(names=self.labels)})

        new_dataset = Dataset.from_dict(new_data, features=self._features)

        # Ensure _dataset_dict is not None (should be initialized by now)
        if self._dataset_dict is None:
            raise RuntimeError("Dataset dictionary was not properly initialized")

        # Concatenate with existing split data
        if split in self._dataset_dict and len(self._dataset_dict[split]) > 0:
            # Use concatenate_datasets function
            self._dataset_dict[split] = concatenate_datasets([self._dataset_dict[split], new_dataset])
        else:
            self._dataset_dict[split] = new_dataset

        # Push updated dataset to hub
        try:
            self._dataset_dict.push_to_hub(
                self.dataset_name,
                token=self.hf_token,
                commit_message=f"Added {len(images)} images to {split} split",
            )
            logger.info(f"Successfully pushed {len(images)} images to {split} split on Hugging Face")
        except Exception as e:
            logger.error(f"Error pushing dataset to Hugging Face: {e}")
            raise

    def load_dataset_from_hub(self) -> DatasetDict:
        """
        Load the dataset from Hugging Face hub.
        Returns the loaded DatasetDict.
        """
        if not self.dataset_name:
            raise ValueError("Dataset name is required but not provided in configuration")

        try:
            from datasets import load_dataset

            loaded_dataset = load_dataset(self.dataset_name, token=self.hf_token)

            # Ensure we have a DatasetDict
            if isinstance(loaded_dataset, DatasetDict):
                self._dataset_dict = loaded_dataset
            elif isinstance(loaded_dataset, Dataset):
                # If it's a single Dataset, wrap it in a DatasetDict
                self._dataset_dict = DatasetDict([("train", loaded_dataset)])
            else:
                # For other types (IterableDataset, etc.), create a new dataset
                raise ValueError(f"Unsupported dataset type: {type(loaded_dataset)}")

            logger.info(f"Successfully loaded dataset from hub: {self.dataset_name}")
            return self._dataset_dict

        except Exception as e:
            logger.error(f"Error loading dataset from hub: {e}")
            raise

    def get_dataset_info(self) -> Dict[str, Union[Optional[str], List[str], Dict[str, Any], int]]:
        """
        Get information about the current dataset.
        Returns a dictionary with dataset statistics.
        """
        if self._dataset_dict is None:
            self.load_dataset_from_hub()

        if self._dataset_dict is None:
            return {"dataset_name": self.dataset_name, "labels": self.labels, "splits": {}, "total_images": 0}

        info = {"dataset_name": self.dataset_name, "labels": self.labels, "splits": {}, "total_images": 0}

        for split_name, split_dataset in self._dataset_dict.items():
            split_info = {"num_images": len(split_dataset), "label_distribution": {}}

            # Count label distribution if dataset is not empty
            if len(split_dataset) > 0:
                label_counts = {}
                for label_idx in split_dataset["label"]:
                    label_name = self.labels[label_idx]
                    label_counts[label_name] = label_counts.get(label_name, 0) + 1
                split_info["label_distribution"] = label_counts

            info["splits"][split_name] = split_info
            info["total_images"] += split_info["num_images"]

        return info

    def save_dataset_locally(self, save_path: str) -> None:
        """
        Save the dataset to a local directory.

        :param save_path: Path to save the dataset
        """
        if self._dataset_dict is None:
            self.load_dataset_from_hub()

        if self._dataset_dict is None:
            raise RuntimeError("No dataset to save")

        try:
            self._dataset_dict.save_to_disk(save_path)
            logger.info(f"Dataset saved locally to: {save_path}")
        except Exception as e:
            logger.error(f"Error saving dataset locally: {e}")
            raise

    def _add_images_memory_efficient(
        self, images: List[Image.Image], labels: List[str], split: str, force_push: bool
    ) -> None:
        """
        Add images using memory-efficient batch processing.
        Images are accumulated until batch_size is reached, then pushed to hub.
        """
        # Add to current batch
        for img, label in zip(images, labels):
            self._current_batch[split].append({"image": img, "label": label})
            self._batch_counts[split] += 1

        logger.info(f"Added {len(images)} images to '{split}' batch (current batch size: {self._batch_counts[split]})")

        # Check if we should push the batch
        if self._batch_counts[split] >= self.batch_size or force_push:
            self._push_batch(split)

    def _push_batch(self, split: str) -> None:
        """Push the current batch for a specific split to Hugging Face."""
        if self._batch_counts[split] == 0:
            logger.info(f"No images in {split} batch to push")
            return

        logger.info(f"Pushing batch of {self._batch_counts[split]} images to {split} split")

        # Create temporary directory for this batch
        with tempfile.TemporaryDirectory(prefix=f"hf_batch_{split}_") as temp_dir:
            # Convert batch to dataset
            batch_data = {
                "image": [item["image"] for item in self._current_batch[split]],
                "label": [item["label"] for item in self._current_batch[split]],
            }

            if self._features is None:
                self._features = Features({"image": HFImage(), "label": ClassLabel(names=self.labels)})

            batch_dataset = Dataset.from_dict(batch_data, features=self._features)

            # Save as parquet file with unique name
            timestamp = int(time.time() * 1000)
            parquet_filename = f"batch_{timestamp}.parquet"
            parquet_path = Path(temp_dir) / split / parquet_filename
            parquet_path.parent.mkdir(exist_ok=True)

            # Save to parquet
            batch_dataset.to_parquet(str(parquet_path))

            # Upload to hub
            try:
                if not self.dataset_name:
                    raise ValueError("Dataset name is required")

                self.api.upload_file(
                    path_or_fileobj=str(parquet_path),
                    path_in_repo=f"{split}/{parquet_filename}",
                    repo_id=self.dataset_name,
                    repo_type="dataset",
                    commit_message=f"Add batch of {self._batch_counts[split]} images to {split} split",
                )
                logger.info(f"Successfully pushed batch to {split} split")

                # Clear the batch
                self._current_batch[split] = []
                self._batch_counts[split] = 0

            except Exception as e:
                logger.error(f"Error pushing batch to hub: {e}")
                raise

    def flush_all_batches(self) -> None:
        """Push all remaining batches to the hub."""
        logger.info("Flushing all remaining batches")
        for split in ["train", "validation", "test"]:
            if self._batch_counts[split] > 0:
                self._push_batch(split)

    def create_streaming_dataset(self) -> Union[IterableDatasetDict, IterableDataset, DatasetDict, Dataset]:
        """
        Create a streaming dataset that doesn't load everything into memory.
        Returns an IterableDataset/IterableDatasetDict that can be used for training.
        Note: The exact return type depends on the dataset structure.
        """
        try:
            if not self.dataset_name:
                raise ValueError("Dataset name is required")

            return load_dataset(
                self.dataset_name,
                token=self.hf_token,
                streaming=True,  # This enables streaming mode
            )
        except Exception as e:
            logger.error(f"Error creating streaming dataset: {e}")
            raise
