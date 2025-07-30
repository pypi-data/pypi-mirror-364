"""
Dataset synchronization utilities for HuggingFace Hub operations.
Provides reusable functions for pulling and pushing datasets with sync strategies.
"""

import json
import logging
import os
import shutil
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from huggingface_hub import HfApi, create_repo, repo_exists, snapshot_download

from .sync_strategy import SyncStrategy

logger = logging.getLogger(__name__)


def pull_dataset_with_strategy(
    dataset_name: str,
    local_path: Path,
    hf_token: Optional[str] = None,
    sync_strategy: SyncStrategy = SyncStrategy.NEVER,
    max_retries: int = 5,
    initial_retry_delay: int = 5,
) -> None:
    """
    Pull a dataset from HuggingFace Hub with configurable sync strategy.
    
    Args:
        dataset_name: Name of the dataset on HuggingFace Hub
        local_path: Local path where dataset should be stored
        hf_token: HuggingFace authentication token
        sync_strategy: Strategy for syncing (ALWAYS, IF_CHANGED, NEVER)
        max_retries: Maximum number of retry attempts
        initial_retry_delay: Initial delay between retries in seconds
    """
    api = HfApi(token=hf_token)

    # If local exists and strategy is NEVER, skip download
    if local_path.exists() and sync_strategy == SyncStrategy.NEVER:
        logger.info(f"Using existing local dataset: {dataset_name} (sync_strategy=NEVER)")
        return

    # Check if repository exists on Hugging Face
    try:
        repo_exists_remote = repo_exists(dataset_name, repo_type="dataset", token=hf_token)
    except Exception as e:
        logger.warning(f"Could not check if repository exists (network issue?): {e}")
        repo_exists_remote = False

    if repo_exists_remote:
        # Handle IF_CHANGED strategy
        if local_path.exists() and sync_strategy == SyncStrategy.IF_CHANGED:
            try:
                # Get repository info to check last modified
                repo_info = api.dataset_info(dataset_name, token=hf_token)
                
                # Check if we have a local metadata file with last sync info
                metadata_file = local_path / ".sync_metadata"
                
                if metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        local_metadata = json.load(f)
                    
                    # Compare last modified dates
                    if local_metadata.get("last_modified") == str(repo_info.last_modified):
                        logger.info(f"Dataset {dataset_name} is up to date (sync_strategy=IF_CHANGED)")
                        return
            except Exception as e:
                logger.warning(f"Could not check if dataset changed: {e}. Will download anyway.")
        
        # Skip download if local exists and strategy is not ALWAYS
        if local_path.exists() and sync_strategy != SyncStrategy.ALWAYS:
            if sync_strategy != SyncStrategy.IF_CHANGED:  # We already handled IF_CHANGED above
                logger.info(f"Skipping download, using local dataset: {dataset_name}")
                return
        
        # Try to download from remote with retries
        logger.info(f"Attempting to sync dataset from Hugging Face: {dataset_name} (sync_strategy={sync_strategy.value})")

        retry_delay = initial_retry_delay

        for attempt in range(max_retries):
            try:
                # Create a temporary download directory
                temp_download_path = local_path.parent / f"{dataset_name.replace('/', '_')}_temp_download"

                # Increase timeout for API operations
                original_timeout = os.environ.get("HF_HUB_DOWNLOAD_TIMEOUT", "10")
                os.environ["HF_HUB_DOWNLOAD_TIMEOUT"] = "120"  # 2 minutes timeout

                try:
                    # Download the dataset to temporary location
                    snapshot_download(
                        repo_id=dataset_name,
                        repo_type="dataset",
                        local_dir=str(temp_download_path),
                        token=hf_token,
                        ignore_patterns=["*.git*"],  # Ignore git files
                        resume_download=True,  # Resume if interrupted
                        max_workers=2,  # Reduce parallel downloads for stability
                    )

                    # If download successful, replace the existing directory
                    if local_path.exists():
                        shutil.rmtree(local_path)
                    shutil.move(str(temp_download_path), str(local_path))

                    # Save metadata for IF_CHANGED strategy
                    if sync_strategy == SyncStrategy.IF_CHANGED:
                        try:
                            repo_info = api.dataset_info(dataset_name, token=hf_token)
                            metadata_file = local_path / ".sync_metadata"
                            with open(metadata_file, 'w') as f:
                                json.dump({
                                    "last_modified": str(repo_info.last_modified),
                                    "last_sync": datetime.now().isoformat()
                                }, f)
                        except Exception as e:
                            logger.warning(f"Could not save sync metadata: {e}")

                    logger.info(f"Successfully synced dataset: {dataset_name}")
                    return  # Success, exit the function

                finally:
                    # Restore original timeout
                    os.environ["HF_HUB_DOWNLOAD_TIMEOUT"] = original_timeout

            except Exception as e:
                # Clean up temp directory if it exists
                temp_download_path = local_path.parent / f"{dataset_name.replace('/', '_')}_temp_download"
                if temp_download_path.exists():
                    shutil.rmtree(temp_download_path)

                if attempt < max_retries - 1:
                    logger.warning(
                        f"Download attempt {attempt + 1} failed: {e}. Retrying in {retry_delay} seconds..."
                    )
                    time.sleep(retry_delay)
                    retry_delay = min(retry_delay * 2, 60)  # Exponential backoff, max 60 seconds
                else:
                    logger.warning(f"All download attempts failed. Last error: {e}")

        # If all retries failed, fall back to local cache
        if not local_path.exists():
            logger.info(f"Creating new local directory for dataset: {dataset_name}")
            local_path.mkdir(parents=True, exist_ok=True)
            # Create README
            readme_path = local_path / "README.md"
            readme_path.write_text(f"# {dataset_name}\n\nDataset for image review process.\n")
        else:
            logger.info(f"Using existing local cache for dataset: {dataset_name}")

    else:
        # Repository doesn't exist on remote
        if not local_path.exists():
            logger.info(f"Dataset does not exist on Hugging Face. Creating new local directory: {dataset_name}")
            local_path.mkdir(parents=True, exist_ok=True)
            # Create README
            readme_path = local_path / "README.md"
            readme_path.write_text(f"# {dataset_name}\n\nDataset for image review process.\n")
        else:
            logger.info(f"Dataset does not exist on Hugging Face. Using existing local directory: {dataset_name}")


def push_dataset_with_retry(
    dataset_name: str,
    local_path: Path,
    hf_token: Optional[str] = None,
    private: bool = True,
    commit_message: Optional[str] = None,
    max_retries: int = 5,
    initial_retry_delay: int = 5,
) -> None:
    """
    Push a dataset to HuggingFace Hub with retry logic.
    
    Args:
        dataset_name: Name of the dataset on HuggingFace Hub
        local_path: Local path of the dataset to push
        hf_token: HuggingFace authentication token
        private: Whether the dataset should be private
        commit_message: Commit message for the push
        max_retries: Maximum number of retry attempts
        initial_retry_delay: Initial delay between retries in seconds
    """
    api = HfApi(token=hf_token)

    if not local_path.exists():
        raise ValueError(f"Local dataset path does not exist: {local_path}")

    # Check if repository exists on Hugging Face
    try:
        repo_exists_remote = repo_exists(dataset_name, repo_type="dataset", token=hf_token)
    except Exception as e:
        logger.error(f"Error checking if repository exists: {e}")
        repo_exists_remote = False

    # Create repository if it doesn't exist
    if not repo_exists_remote:
        logger.info(f"Creating dataset repository on Hugging Face: {dataset_name}")
        try:
            create_repo(dataset_name, repo_type="dataset", private=private, token=hf_token)
            logger.info(f"Successfully created dataset repository: {dataset_name}")
        except Exception as e:
            logger.error(f"Error creating dataset repository: {e}")
            raise

    # Generate commit message if not provided
    if commit_message is None:
        commit_message = f"Update dataset - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    # Upload the dataset using HuggingFace Hub API with retries
    logger.info(f"Uploading dataset to Hugging Face: {dataset_name}")

    retry_delay = initial_retry_delay

    for attempt in range(max_retries):
        try:
            # Increase timeout for upload operations
            original_timeout = os.environ.get("HF_HUB_UPLOAD_TIMEOUT", "300")
            os.environ["HF_HUB_UPLOAD_TIMEOUT"] = "600"  # 10 minutes timeout

            try:
                # Upload the entire folder
                api.upload_folder(
                    folder_path=str(local_path),
                    repo_id=dataset_name,
                    repo_type="dataset",
                    token=hf_token,
                    commit_message=commit_message,
                    ignore_patterns=[".git*", "*.pyc", "__pycache__", ".sync_metadata"],
                )

                logger.info(f"Successfully uploaded dataset to Hugging Face: {dataset_name}")
                return  # Success, exit the function

            finally:
                # Restore original timeout
                os.environ["HF_HUB_UPLOAD_TIMEOUT"] = original_timeout

        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(f"Upload attempt {attempt + 1} failed: {e}. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, 60)  # Exponential backoff, max 60 seconds
            else:
                logger.error(f"All upload attempts failed. Last error: {e}")
                raise
