"""
Utility function for pushing raw folders to Hugging Face Hub.
"""
import subprocess
import os
import logging
from pathlib import Path
from huggingface_hub import HfApi


logger = logging.getLogger(__name__)


def push_raw_folder_to_hugging_face(
    dataset_name: str,
    local_dataset_path: Path,
    hf_token: str,
    private: bool = True,
    commit_message: str = "Update dataset",
    use_cli_for_upload: bool = False,
) -> None:
    """
    Push a raw folder to Hugging Face Hub without any transformation.
    This function uploads all files in the folder structure as-is.

    Args:
        dataset_name (str): Name of the dataset on Hugging Face (e.g., "username/dataset-name")
        local_dataset_path (Path): Path to the local folder to push
        hf_token (str): Hugging Face authentication token
        private (bool): Whether the dataset should be private (default: True)
        commit_message (str): Commit message for the push (default: "Update dataset")
        push_with_cli (bool): Use huggingface-cli command instead of Python SDK (default: False)
    """
    if not local_dataset_path.exists():
        raise ValueError(f"Dataset path {local_dataset_path} does not exist")

    if not local_dataset_path.is_dir():
        raise ValueError(f"Dataset path {local_dataset_path} must be a directory")

    logger.info(f"📦 Preparing to push raw folder from {local_dataset_path} to {dataset_name}")

    if use_cli_for_upload:
        # Use huggingface-cli command for large datasets
        logger.info("🔧 Using huggingface-cli command for upload (suitable for large datasets)")
        
        
        
        # Set the HF token as environment variable for the CLI
        env = os.environ.copy()
        env["HF_TOKEN"] = hf_token
        
        # Build the command
        # Example: huggingface-cli upload Logiroad/detectors_dummy_data .cache/Logiroad/detectors_dummy_data --repo-type dataset --commit-message "Update detectors dataset"
        cmd = [
            "huggingface-cli",
            "upload",
            dataset_name,
            str(local_dataset_path),
            "--repo-type", "dataset",
            "--commit-message", commit_message
        ]
        
        if private:
            # Note: huggingface-cli doesn't have a --private flag, so we need to create the repo first
            try:
                api = HfApi(token=hf_token)
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
        
        # Execute the command
        try:
            logger.info(f"🚀 Executing command: {' '.join(cmd)}")
            
            # Run the command with real-time output
            process = subprocess.Popen(
                cmd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            # Stream output in real-time
            if process.stdout:
                for line in process.stdout:
                    if line.strip():
                        logger.info(f"  CLI: {line.strip()}")
            
            # Wait for completion and check return code
            return_code = process.wait()
            
            if return_code == 0:
                logger.info(f"✅ Successfully pushed raw folder to {dataset_name} using CLI")
                logger.info(f"🔗 View dataset at: https://huggingface.co/datasets/{dataset_name}")
            else:
                raise RuntimeError(f"huggingface-cli command failed with return code {return_code}")
                
        except Exception as e:
            logger.error(f"❌ Failed to push folder using huggingface-cli: {e}")
            logger.error("💡 Make sure huggingface-cli is installed: pip install huggingface-hub[cli]")
            raise
    else:
        # Use Python API (original implementation)
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

        # Collect all files to upload
        files_to_upload = []
        total_size = 0

        for file_path in local_dataset_path.rglob("*"):
            if file_path.is_file():
                # Calculate relative path from the dataset root
                relative_path = file_path.relative_to(local_dataset_path)
                files_to_upload.append((file_path, relative_path))
                total_size += file_path.stat().st_size

        if not files_to_upload:
            logger.warning(f"⚠️ No files found to upload in {local_dataset_path}")
            return

        logger.info(f"📊 Found {len(files_to_upload)} files to upload (total size: {total_size / 1024 / 1024:.2f} MB)")

        # Upload files
        try:
            logger.info(f"🚀 Uploading files to {dataset_name}...")
            
            if len(files_to_upload) > 1000:
                logger.info(f"📊 Large dataset detected ({len(files_to_upload)} files, {total_size / 1024 / 1024 / 1024:.2f} GB)")
                logger.info("⚠️  This may take a while. The upload might fail due to timeouts with very large datasets.")

            # Upload all files at once using upload_folder
            api.upload_folder(
                folder_path=str(local_dataset_path),
                repo_id=dataset_name,
                repo_type="dataset",
                token=hf_token,
                commit_message=commit_message,
            )

            logger.info(f"✅ Successfully pushed raw folder to {dataset_name}")
            logger.info(f"🔗 View dataset at: https://huggingface.co/datasets/{dataset_name}")
        except Exception as e:
            logger.error(f"❌ Failed to push folder to Hugging Face: {e}")
            # Provide more helpful error messages for common issues
            if "Error while uploading" in str(e) or "RuntimeError" in str(e):
                logger.error("💡 This often happens with large datasets. Try:")
                logger.error("   1. Check your internet connection stability")
                logger.error("   2. Ensure you have enough disk space")
                logger.error("   3. Use the Hugging Face CLI instead: huggingface-cli upload --repo-type dataset")
                logger.error(f"      Example: huggingface-cli upload {dataset_name} {local_dataset_path} --repo-type dataset")
                logger.error("   4. For very large datasets (>10GB), consider uploading in smaller chunks")
                logger.error("   5. Use Git LFS directly for more control over the upload process")
            raise
