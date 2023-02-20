# log_archiver module


### log_archiver.check_object_is_missing(files_to_upload: Dict[str, str], files_to_remove: Set[str], bucket: str)
Checks if remote_file_path exists in S3 Bucket. If it does, then file is removed as a candidate.
:param files_to_remove: Set of files which are candidates for removal
:param files_to_upload: Dictionary of files which are candidates for upload.
:param bucket: Name of S3 Bucket where files will be uploaded to.
:return:


### log_archiver.compress_file(files_to_compress: Set[str], files_to_upload: Dict[str, str], hostname: str, dry_run: bool)
Compresses file into GZIP format and adds as candidate to files_to_upload
:param files_to_compress: Set of file paths which need to be compressed
:param files_to_upload: Dictionary of absolute file path : remote file path
:param hostname: hostname for namespace purposes
:param dry_run: indicates whether to perform compression.
:return:


### log_archiver.create_remote_path(files_to_upload: Dict[str, str], business_unit: str, environment: str)
Given a dictionary of paths, the function will construct the remote path / S3 URI for each path.
:param files_to_upload: Dictionary of files which are candidates for upload.
:param business_unit: namespace representing business unit associated with application log.
:param environment: namespace representing SDLC associated with application log.
:return:


### log_archiver.find_files(path: List[str], now: float, log_expiry_age_days: int)
Given a path, it will search file-system for candidates of files that need to be compressed.
:param path: Path string to search for files.
:param now: Float used as comparison for candidate check.
:param log_expiry_age_days:
:return: files_to_compress, files_to_upload, files_to_remove


### log_archiver.handler(\*\*kwargs)
Main function for log_archiver
:param kwargs:
:return:


### log_archiver.remove_date_check(abs_file_path: str, now: float, log_expiry_age_days: int)
Returns True if GZIP file is older than log_expiry_age_days.
:param abs_file_path: absolute file path to assess
:param now: time when process began execution.
:param log_expiry_age_days: Criteria for expiring logs.
:return:


### log_archiver.remove_file(files_to_remove: set[str])
Removes file when given set of file paths.
:param files_to_remove: absolute file paths
:return: None


### log_archiver.summary_logging(files_to_upload: Dict[str, str], files_to_compress: Set[str], files_to_remove: Set[str])
Provides a summary report of files uploaded, compressed and removed.
:param files_to_upload: Dictionary of files which are candidates for upload.
:param files_to_compress: Set of file paths which need to be compressed
:param files_to_remove: Set of files which are candidates for removal
:return:


### log_archiver.upload_s3(files_to_upload: Dict[str, str], bucket: str, files_to_remove: Set[str], now: float, log_expiry_age_days: int)
Uploads file to S3 bucket and add candidates for removal.
:param files_to_upload: Dictionary of absolute file path : remote file path
:param bucket: Name of S3 bucket
:param files_to_remove: Files that are candidates for removal.
:param now: time when process began execution.
:param log_expiry_age_days: Criteria for expiring logs.
:return: None
