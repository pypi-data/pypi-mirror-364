"""
Download Manager for PhysioNet Databases

Handles downloading datasets using different methods (wget, AWS S3, WFDB)
based on database requirements and access permissions with real-time progress tracking.
"""

import asyncio
import logging
import shutil
import subprocess
import time
import re
from pathlib import Path
from typing import Dict, List, Any, Callable
from concurrent.futures import ThreadPoolExecutor
import wfdb

from .database_registry import (
    DatabaseInfo,
    DownloadMethod,
    AccessType,
    get_database_info,
)
from .config import ServerConfig


logger = logging.getLogger(__name__)


class DownloadProgress:
    """Class to track and report download progress."""

    def __init__(self, database_name: str, total_size_mb: float = None):
        self.database_name = database_name
        self.total_size_mb = total_size_mb
        self.downloaded_mb = 0.0
        self.files_downloaded = 0
        self.total_files = None
        self.start_time = time.time()
        self.status = "starting"
        self.error_message = None

    def update(
        self, downloaded_mb: float = None, files_count: int = None, status: str = None
    ):
        """Update progress metrics."""
        if downloaded_mb is not None:
            self.downloaded_mb = downloaded_mb
        if files_count is not None:
            self.files_downloaded = files_count
        if status is not None:
            self.status = status

        # Log progress update for Claude Desktop to see
        progress_percent = 0
        if self.total_size_mb and self.total_size_mb > 0:
            progress_percent = min((self.downloaded_mb / self.total_size_mb) * 100, 100)
        elif self.total_files and self.total_files > 0:
            progress_percent = min(
                (self.files_downloaded / self.total_files) * 100, 100
            )

        elapsed_time = time.time() - self.start_time
        speed_mbps = self.downloaded_mb / elapsed_time if elapsed_time > 0 else 0

        logger.info(
            f"📥 {self.database_name}: {progress_percent:.1f}% ({self.downloaded_mb:.1f}/{self.total_size_mb or '?'} MB) "
            f"[{self.files_downloaded} files] [{speed_mbps:.1f} MB/s] - {self.status}"
        )

    def complete(self, success: bool = True, error: str = None):
        """Mark download as completed."""
        elapsed_time = time.time() - self.start_time
        if success:
            self.status = "completed"
            logger.info(
                f"✅ {self.database_name}: Download completed in {elapsed_time:.1f}s "
                f"({self.downloaded_mb:.1f} MB, {self.files_downloaded} files)"
            )
        else:
            self.status = "failed"
            self.error_message = error
            logger.error(
                f"❌ {self.database_name}: Download failed after {elapsed_time:.1f}s - {error}"
            )


class DownloadError(Exception):
    """Exception raised when download fails."""

    pass


class DownloadManager:
    """Manages downloading PhysioNet databases with different access methods."""

    def __init__(self, config: ServerConfig):
        self.config = config
        self.auth = config.auth
        self.executor = ThreadPoolExecutor(max_workers=config.max_concurrent_downloads)
        self.active_downloads: Dict[str, DownloadProgress] = {}

    async def ensure_database(
        self, db_info: DatabaseInfo, progress_callback: Callable = None
    ) -> bool:
        """Ensure a database is available locally, downloading if necessary."""
        db_path = self.config.get_database_path(db_info.name)

        # Check if already downloaded and valid
        if self._is_download_complete(db_info):
            logger.info(f"📁 Database {db_info.name} already exists at {db_path}")
            return True

        logger.info(f"🚀 Starting download of {db_info.name} to {db_path}")

        # Initialize progress tracking
        progress = DownloadProgress(
            db_info.name, db_info.size_gb * 1024 if db_info.size_gb else None
        )
        self.active_downloads[db_info.name] = progress
        progress.update(status="initializing")

        try:
            # Ensure directory exists
            db_path.mkdir(parents=True, exist_ok=True)

            # Download based on method
            if db_info.download_method == DownloadMethod.WGET:
                await self._download_with_wget(db_info, db_path, progress)
            elif db_info.download_method == DownloadMethod.AWS_S3:
                await self._download_with_s3(db_info, db_path, progress)
            elif db_info.download_method == DownloadMethod.WFDB:
                await self._download_with_wfdb(db_info, db_path, progress)
            else:
                raise DownloadError(
                    f"Unsupported download method: {db_info.download_method}"
                )

            progress.complete(success=True)
            return True

        except Exception as e:
            error_msg = f"Download failed for {db_info.name}: {e}"
            progress.complete(success=False, error=str(e))
            logger.error(error_msg)

            # Clean up partial download
            if db_path.exists():
                try:
                    shutil.rmtree(db_path)
                    logger.info(f"🧹 Cleaned up partial download for {db_info.name}")
                except Exception as cleanup_error:
                    logger.warning(
                        f"Failed to clean up partial download: {cleanup_error}"
                    )

            raise DownloadError(error_msg)
        finally:
            # Remove from active downloads
            self.active_downloads.pop(db_info.name, None)

    def _is_download_complete(self, db_info: DatabaseInfo) -> bool:
        """Check if download is complete and valid, supporting caching."""
        db_path = self.config.get_database_path(db_info.name)

        if not db_path.exists():
            return False

        # Check expected files if specified
        if db_info.expected_files:
            missing_files = []
            for expected_file in db_info.expected_files:
                file_path = db_path / expected_file
                if not file_path.exists():
                    missing_files.append(expected_file)

            if missing_files:
                logger.warning(
                    f"📋 Missing expected files for {db_info.name}: {missing_files[:3]}..."
                )
                return False

        # Check if directory has substantial content
        try:
            files = list(db_path.rglob("*"))
            file_count = len([f for f in files if f.is_file()])
            total_size_mb = sum(f.stat().st_size for f in files if f.is_file()) / (
                1024 * 1024
            )

            if file_count < 3:  # Too few files
                logger.warning(f"📊 Too few files in {db_info.name}: {file_count}")
                return False

            if total_size_mb < 1:  # Too small
                logger.warning(
                    f"📏 Download too small for {db_info.name}: {total_size_mb:.1f} MB"
                )
                return False

            logger.info(
                f"✅ Cache hit for {db_info.name}: {file_count} files, {total_size_mb:.1f} MB"
            )
            return True

        except Exception as e:
            logger.error(f"Error validating download for {db_info.name}: {e}")
            return False

    async def _download_with_wget(
        self, db_info: DatabaseInfo, target_path: Path, progress: DownloadProgress
    ) -> None:
        """Download using wget with progress tracking."""
        if not db_info.base_url:
            raise DownloadError(f"No base URL specified for {db_info.name}")

        progress.update(status="downloading")

        # Build wget command using proven working format
        cmd = [
            "wget",
            "-r",  # Recursive
            "-N",  # Only download newer files
            "-c",  # Continue partial downloads
            "-np",  # No parent directories
            "--progress=bar:force",  # Force progress output
            db_info.base_url,
        ]

        # Add authentication if required
        if db_info.access_type == AccessType.CREDENTIALED and self.auth.username:
            cmd.extend(
                ["--user", self.auth.username, "--password", self.auth.password or ""]
            )

        # Change to target directory so wget downloads there directly
        original_cwd = Path.cwd()
        try:
            target_path.mkdir(parents=True, exist_ok=True)
            import os

            os.chdir(target_path)

            # Run with progress monitoring
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                self.executor, self._run_subprocess_with_progress, cmd, progress
            )

        finally:
            # Always restore original directory
            os.chdir(original_cwd)

        # wget creates nested directories matching the URL structure
        # Move files to flatten the structure if needed
        from urllib.parse import urlparse

        parsed_url = urlparse(db_info.base_url)
        downloaded_path = target_path / parsed_url.netloc / parsed_url.path.strip("/")

        if downloaded_path.exists() and downloaded_path != target_path:
            progress.update(status="organizing files")

            # Move contents to target path
            for item in downloaded_path.rglob("*"):
                if item.is_file():
                    # Maintain directory structure relative to downloaded_path
                    rel_path = item.relative_to(downloaded_path)
                    dest_file = target_path / rel_path
                    dest_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(item), str(dest_file))

            # Clean up empty wget directory structure
            import shutil as shutil_module

            try:
                shutil_module.rmtree(target_path / parsed_url.netloc)
            except Exception:
                pass

        # Final progress update
        self._update_progress_from_path(progress, target_path)

    async def _download_with_s3(
        self, db_info: DatabaseInfo, target_path: Path, progress: DownloadProgress
    ) -> None:
        """Download using AWS S3 sync with progress tracking."""
        if not db_info.s3_bucket:
            raise DownloadError(f"No S3 bucket specified for {db_info.name}")

        progress.update(status="downloading")

        s3_url = f"s3://physionet-open/{db_info.s3_bucket}/"
        cmd = [
            "aws",
            "s3",
            "sync",
            "--no-sign-request",  # Public bucket, no credentials needed
            s3_url,
            str(target_path),
        ]

        # Add options for efficient transfer
        if self.config.resume_downloads:
            cmd.append("--exclude")
            cmd.append("*.tmp")  # Skip temporary files

        # Run with progress monitoring
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            self.executor, self._run_subprocess_with_progress, cmd, progress
        )

    async def _download_with_wfdb(
        self, db_info: DatabaseInfo, target_path: Path, progress: DownloadProgress
    ) -> None:
        """Download using WFDB Python library with progress tracking."""
        if not db_info.wfdb_database:
            raise DownloadError(f"No WFDB database specified for {db_info.name}")

        progress.update(status="downloading")

        # Use thread pool for WFDB operations
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            self.executor, self._download_wfdb_records, db_info, target_path, progress
        )

    def _run_subprocess_with_progress(
        self, cmd: List[str], download_progress: DownloadProgress
    ) -> None:
        """Run a subprocess command with progress monitoring."""
        logger.debug(f"Running command with progress: {' '.join(cmd)}")

        try:
            # Start the process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # Combine stderr with stdout
                text=True,
                bufsize=1,  # Line-buffered output
                universal_newlines=True,
            )

            # Read and parse progress output
            for line in iter(process.stdout.readline, ""):
                line = line.strip()
                if not line:
                    continue

                # Parse wget progress
                if "%" in line and "[" in line:
                    # Look for patterns like "50% [======>     ] 1,024,000 bytes in 5.2s (197 KB/s)"
                    match = re.search(r"(\d+)%", line)
                    if match:
                        percent = float(match.group(1))

                        # Extract downloaded size
                        size_match = re.search(r"([\d,]+)\s*bytes", line)
                        if size_match:
                            size_bytes = float(size_match.group(1).replace(",", ""))
                            size_mb = size_bytes / (1024 * 1024)
                            download_progress.update(
                                downloaded_mb=size_mb,
                                status=f"downloading ({percent}%)",
                            )

                # Parse AWS S3 progress
                elif "download:" in line or "upload:" in line:
                    # Count files
                    download_progress.files_downloaded += 1
                    download_progress.update(
                        files_count=download_progress.files_downloaded,
                        status="downloading files",
                    )

                # Log other interesting output
                if any(
                    keyword in line.lower()
                    for keyword in ["error", "failed", "complete", "finished"]
                ):
                    logger.debug(f"Download progress: {line}")

            # Wait for process to complete
            return_code = process.wait()
            if return_code != 0:
                raise DownloadError(f"Command failed with exit code {return_code}")

        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed: {e}")
            raise DownloadError(f"Subprocess failed: {e}")
        except subprocess.TimeoutExpired:
            raise DownloadError("Download timed out")
        except Exception as e:
            logger.error(f"Error during subprocess progress monitoring: {e}")
            raise DownloadError(f"Subprocess failed: {e}")
        finally:
            # Ensure process is cleaned up
            try:
                process.stdout.close()
                if process.poll is None:
                    process.terminate()
            except Exception:
                pass

    def _download_wfdb_records(
        self,
        db_info: DatabaseInfo,
        target_path: Path,
        download_progress: DownloadProgress,
    ) -> None:
        """Download WFDB records using the WFDB library."""
        try:
            # Get list of records in the database
            records = wfdb.get_record_list(db_info.wfdb_database)

            logger.info(f"Found {len(records)} records in {db_info.wfdb_database}")
            download_progress.total_files = len(records)

            # Download records with progress tracking
            for i, record in enumerate(records):
                try:
                    # Update progress
                    download_progress.update(
                        files_count=i,
                        status=f"downloading record {record} ({i + 1}/{len(records)})",
                    )

                    # Download record and annotation files
                    wfdb.rdsamp(
                        record,
                        pn_dir=db_info.wfdb_database,
                        return_res=16,  # Return in 16-bit format
                        channel_names=None,
                    )

                    # Move downloaded files to target directory
                    record_files = Path.cwd().glob(f"{record}.*")
                    for file_path in record_files:
                        target_file = target_path / file_path.name
                        shutil.move(str(file_path), str(target_file))

                except Exception as e:
                    logger.warning(f"Failed to download record {record}: {e}")
                    continue

            # Final update
            download_progress.update(files_count=len(records), status="completed")

        except Exception as e:
            raise DownloadError(f"WFDB download failed: {e}")

    def _update_progress_from_path(
        self, progress: DownloadProgress, target_path: Path
    ) -> None:
        """Update progress based on the actual downloaded files and size."""
        try:
            files = list(target_path.rglob("*"))
            file_count = len([f for f in files if f.is_file()])
            total_size_mb = sum(f.stat().st_size for f in files if f.is_file()) / (
                1024 * 1024
            )

            progress.update(
                downloaded_mb=total_size_mb,
                files_count=file_count,
                status="organizing files",
            )

        except Exception as e:
            logger.error(
                f"Error updating progress from path for {progress.database_name}: {e}"
            )
            progress.update(status="error")

    async def download_multiple(self, db_infos: List[DatabaseInfo]) -> Dict[str, bool]:
        """Download multiple databases concurrently."""
        results = {}

        # Create semaphore to limit concurrent downloads
        semaphore = asyncio.Semaphore(self.config.max_concurrent_downloads)

        async def download_with_semaphore(db_info: DatabaseInfo) -> tuple[str, bool]:
            async with semaphore:
                try:
                    success = await self.ensure_database(db_info)
                    return db_info.name, success
                except Exception as e:
                    logger.error(f"Download failed for {db_info.name}: {e}")
                    return db_info.name, False

        # Start all downloads
        tasks = [download_with_semaphore(db_info) for db_info in db_infos]
        completed = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        for result in completed:
            if isinstance(result, Exception):
                logger.error(f"Download task failed: {result}")
            else:
                db_name, success = result
                results[db_name] = success

        return results

    def verify_download(self, db_info: DatabaseInfo) -> bool:
        """Verify that a download completed successfully."""
        db_path = self.config.get_database_path(db_info.name)

        if not db_path.exists():
            return False

        # Check expected files if specified
        if db_info.expected_files:
            for expected_file in db_info.expected_files[:5]:  # Check first 5
                if not (db_path / expected_file).exists():
                    logger.warning(f"Missing expected file: {expected_file}")
                    return False

        # Basic check: ensure directory has content
        try:
            files = list(db_path.iterdir())
            if not files:
                return False
        except Exception:
            return False

        return True

    def get_download_progress(self, db_name: str) -> Dict[str, Any]:
        """Get download progress information for a database."""
        db_path = self.config.get_database_path(db_name)

        if not db_path.exists():
            return {"status": "not_started", "progress": 0.0}

        # Estimate progress based on file count (crude but functional)
        try:
            files = list(db_path.rglob("*"))
            file_count = len([f for f in files if f.is_file()])

            # Very rough estimation - could be improved with size-based calculation
            if file_count < 10:
                status = "downloading"
                progress = min(file_count / 10.0, 0.9)
            else:
                status = "completed"
                progress = 1.0

            return {
                "status": status,
                "progress": progress,
                "file_count": file_count,
                "size_mb": sum(f.stat().st_size for f in files if f.is_file())
                / (1024 * 1024),
            }

        except Exception as e:
            logger.error(f"Error checking download progress: {e}")
            return {"status": "error", "progress": 0.0}

    def cleanup_failed_download(self, db_name: str) -> bool:
        """Clean up files from a failed download."""
        db_path = self.config.get_database_path(db_name)

        try:
            if db_path.exists():
                shutil.rmtree(db_path)
                logger.info(f"🧹 Cleaned up failed download for {db_name}")
                return True
        except Exception as e:
            logger.error(f"Failed to clean up {db_name}: {e}")

        return False

    def get_cache_info(self) -> Dict[str, Any]:
        """Get comprehensive information about the download cache."""
        cache_info = {
            "cache_root": str(self.config.data_root),
            "total_databases": 0,
            "cached_databases": [],
            "total_size_mb": 0.0,
            "total_files": 0,
        }

        try:
            if not self.config.data_root.exists():
                return cache_info

            for db_path in self.config.data_root.iterdir():
                if db_path.is_dir():
                    try:
                        files = list(db_path.rglob("*"))
                        file_count = len([f for f in files if f.is_file()])
                        size_mb = sum(
                            f.stat().st_size for f in files if f.is_file()
                        ) / (1024 * 1024)

                        if file_count > 0:  # Only count non-empty directories
                            cache_info["cached_databases"].append(
                                {
                                    "name": db_path.name,
                                    "files": file_count,
                                    "size_mb": size_mb,
                                    "last_modified": db_path.stat().st_mtime,
                                }
                            )

                            cache_info["total_size_mb"] += size_mb
                            cache_info["total_files"] += file_count
                            cache_info["total_databases"] += 1

                    except Exception as e:
                        logger.warning(
                            f"Error reading cache info for {db_path.name}: {e}"
                        )
                        continue

            # Sort by size (largest first)
            cache_info["cached_databases"].sort(
                key=lambda x: x["size_mb"], reverse=True
            )

            logger.info(
                f"📊 Cache summary: {cache_info['total_databases']} databases, "
                f"{cache_info['total_size_mb']:.1f} MB, {cache_info['total_files']} files"
            )

        except Exception as e:
            logger.error(f"Error getting cache info: {e}")
            cache_info["error"] = str(e)

        return cache_info

    def clear_cache(
        self, database_names: List[str] = None, confirm: bool = False
    ) -> Dict[str, Any]:
        """Clear cached downloads for specified databases or all databases."""
        if not confirm:
            return {
                "error": "Cache clearing requires confirmation. Set confirm=True to proceed.",
                "warning": "This will permanently delete downloaded data!",
            }

        results = {
            "cleared": [],
            "failed": [],
            "total_freed_mb": 0.0,
            "total_files_removed": 0,
        }

        try:
            # If no specific databases specified, clear all
            if not database_names:
                if self.config.data_root.exists():
                    database_names = [
                        d.name for d in self.config.data_root.iterdir() if d.is_dir()
                    ]

            for db_name in database_names:
                try:
                    db_path = self.config.get_database_path(db_name)

                    if db_path.exists():
                        # Calculate size before deletion
                        files = list(db_path.rglob("*"))
                        file_count = len([f for f in files if f.is_file()])
                        size_mb = sum(
                            f.stat().st_size for f in files if f.is_file()
                        ) / (1024 * 1024)

                        # Remove the directory
                        shutil.rmtree(db_path)

                        results["cleared"].append(
                            {
                                "database": db_name,
                                "size_mb": size_mb,
                                "files": file_count,
                            }
                        )

                        results["total_freed_mb"] += size_mb
                        results["total_files_removed"] += file_count

                        logger.info(
                            f"🗑️ Cleared cache for {db_name}: {size_mb:.1f} MB, {file_count} files"
                        )
                    else:
                        logger.warning(f"Cache not found for {db_name}")

                except Exception as e:
                    error_msg = f"Failed to clear cache for {db_name}: {e}"
                    logger.error(error_msg)
                    results["failed"].append({"database": db_name, "error": str(e)})

            logger.info(
                f"🧹 Cache clearing complete: freed {results['total_freed_mb']:.1f} MB, "
                f"removed {results['total_files_removed']} files"
            )

        except Exception as e:
            logger.error(f"Error during cache clearing: {e}")
            results["error"] = str(e)

        return results

    def verify_cache_integrity(
        self, database_names: List[str] = None
    ) -> Dict[str, Any]:
        """Verify the integrity of cached downloads."""
        results = {"verified": [], "corrupted": [], "missing": [], "total_checked": 0}

        try:
            # Default to all configured databases
            if not database_names:
                database_names = self.config.databases

            for db_name in database_names:
                try:
                    results["total_checked"] += 1
                    db_info = get_database_info(db_name)

                    if not db_info:
                        results["missing"].append(
                            {
                                "database": db_name,
                                "reason": "Database not found in registry",
                            }
                        )
                        continue

                    if self._is_download_complete(db_info):
                        # Get actual cache stats
                        db_path = self.config.get_database_path(db_name)
                        files = list(db_path.rglob("*"))
                        file_count = len([f for f in files if f.is_file()])
                        size_mb = sum(
                            f.stat().st_size for f in files if f.is_file()
                        ) / (1024 * 1024)

                        results["verified"].append(
                            {
                                "database": db_name,
                                "files": file_count,
                                "size_mb": size_mb,
                                "status": "valid",
                            }
                        )

                        logger.info(
                            f"✅ {db_name} cache is valid: {file_count} files, {size_mb:.1f} MB"
                        )
                    else:
                        results["corrupted"].append(
                            {"database": db_name, "reason": "Failed integrity check"}
                        )

                        logger.warning(f"⚠️ {db_name} cache may be corrupted")

                except Exception as e:
                    error_msg = f"Error verifying {db_name}: {e}"
                    logger.error(error_msg)
                    results["corrupted"].append({"database": db_name, "reason": str(e)})

            logger.info(
                f"🔍 Cache verification complete: {len(results['verified'])} valid, "
                f"{len(results['corrupted'])} corrupted, {len(results['missing'])} missing"
            )

        except Exception as e:
            logger.error(f"Error during cache verification: {e}")
            results["error"] = str(e)

        return results

    def get_download_progress_info(self, db_name: str) -> Dict[str, Any]:
        """Get real-time download progress for a specific database."""
        if db_name in self.active_downloads:
            progress = self.active_downloads[db_name]
            elapsed = time.time() - progress.start_time

            return {
                "database": db_name,
                "status": progress.status,
                "downloaded_mb": progress.downloaded_mb,
                "total_size_mb": progress.total_size_mb,
                "files_downloaded": progress.files_downloaded,
                "total_files": progress.total_files,
                "elapsed_seconds": elapsed,
                "progress_percent": (
                    progress.downloaded_mb / progress.total_size_mb * 100
                )
                if progress.total_size_mb
                else 0,
                "error_message": progress.error_message,
            }
        else:
            # Check if already complete
            db_info = get_database_info(db_name)
            if db_info and self._is_download_complete(db_info):
                return {
                    "database": db_name,
                    "status": "completed",
                    "progress_percent": 100,
                }
            else:
                return {
                    "database": db_name,
                    "status": "not_started",
                    "progress_percent": 0,
                }
