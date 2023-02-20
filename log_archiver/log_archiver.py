import glob
import gzip
import logging
import os
import re
import socket
import time

import boto3
from botocore.errorfactory import ClientError
from typing import Dict, Set, List

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

logging.basicConfig(format="[%(asctime)s] [%(levelname)s] [%(threadName)s] - %(message)s")

s3_resource = boto3.resource('s3')
s3_client = boto3.client('s3')


def upload_s3(files_to_upload: Dict[str, str], bucket: str, files_to_remove: Set[str], now: float,
              log_expiry_age_days: int) -> None:
    """
    Uploads file to S3 bucket and add candidates for removal.
    :param files_to_upload: Dictionary of absolute file path : remote file path
    :param bucket: Name of S3 bucket
    :param files_to_remove: Files that are candidates for removal.
    :param now: time when process began execution.
    :param log_expiry_age_days: Criteria for expiring logs.
    :return: None
    """
    for abs_file_path in files_to_upload:
        s3_resource.Bucket(bucket).upload_file(abs_file_path, files_to_upload[abs_file_path])
        logger.info(f"Uploaded {abs_file_path} to remote storage")
        if remove_date_check(abs_file_path, now, log_expiry_age_days):
            files_to_remove.add(abs_file_path)
        uncompressed_path = '.'.join(abs_file_path.split('.')[:-2])
        if os.path.exists(uncompressed_path):
            files_to_remove.add(uncompressed_path)


def remove_file(files_to_remove: set[str]) -> None:
    """
    Removes file when given set of file paths.
    :param files_to_remove: absolute file paths
    :return: None
    """
    for abs_file_path in files_to_remove:
        os.remove(abs_file_path)
        logger.info(f"Removed {abs_file_path}")


def compress_file(files_to_compress: Set[str], files_to_upload: Dict[str, str], hostname: str, dry_run: bool) -> None:
    """
    Compresses file into GZIP format and adds as candidate to files_to_upload
    :param files_to_compress: Set of file paths which need to be compressed
    :param files_to_upload: Dictionary of absolute file path : remote file path
    :param hostname: hostname for namespace purposes
    :param dry_run: indicates whether to perform compression.
    :return:
    """
    for abs_file_path in files_to_compress:
        if not dry_run:
            with open(abs_file_path, 'rb') as orig_file:
                with gzip.open(f"{abs_file_path}.{hostname}.gz", 'wb') as zipped_file:
                    zipped_file.writelines(orig_file)
        files_to_upload[abs_file_path + "." + hostname + ".gz"] = ""


def remove_date_check(abs_file_path: str, now: float, log_expiry_age_days: int) -> bool:
    """
    Returns True if GZIP file is older than log_expiry_age_days.
    :param abs_file_path: absolute file path to assess
    :param now: time when process began execution.
    :param log_expiry_age_days: Criteria for expiring logs.
    :return:
    """
    log_name = abs_file_path.split('/')[-1]
    logger.info(log_name)
    date_time = log_name.split('.')[-4]
    pattern = "%Y-%m-%d"
    epoch_file = int(time.mktime(time.strptime(date_time, pattern)))
    logger.info(abs_file_path + " " + str(epoch_file))
    return now - epoch_file >= (log_expiry_age_days * 86400)


def find_files(path: List[str], now: float, log_expiry_age_days: int) -> tuple[set[str], dict[str, str], set[str]]:
    """
    Given a path, it will search file-system for candidates of files that need to be compressed.
    :param path: Path string to search for files.
    :param now: Float used as comparison for candidate check.
    :param log_expiry_age_days:
    :return: files_to_compress, files_to_upload, files_to_remove
    """
    files_to_compress = set()
    files_to_upload = {}
    files_to_remove = set()

    logger.info(f"Finding uncompressed files in {path}")
    for folder in path:
        for f in os.listdir(folder):
            abs_file_path = os.path.join(folder, f)
            valid_format_uncompressed = re.search(r'\.\d{4}-\d{2}-\d{2}.log$', f)
            valid_format_compressed = re.search(r'\.\d{4}-\d{2}-\d{2}.log.gz$', f)

            upload_date_check = os.stat(abs_file_path).st_mtime < now - (1 * 60)

            if os.path.isfile(abs_file_path):
                if valid_format_uncompressed and upload_date_check:
                    files_to_compress.add(abs_file_path)
                    logger.info(f"Adding {abs_file_path} to compression queue.")
                elif valid_format_compressed:
                    files_to_upload[abs_file_path] = None
                    logger.info(f"Adding {abs_file_path} to upload queue.")
                    if remove_date_check(abs_file_path, now, log_expiry_age_days):
                        files_to_remove.add(abs_file_path)
                        logger.info(f"Adding {abs_file_path} to remove queue.")
                else:
                    logger.info(f"Skipping {abs_file_path}")

    return files_to_compress, files_to_upload, files_to_remove


def create_remote_path(files_to_upload: Dict[str, str], business_unit: str, environment: str) -> None:
    """
    Given a dictionary of paths, the function will construct the remote path / S3 URI for each path.
    :param files_to_upload: Dictionary of files which are candidates for upload.
    :param business_unit: namespace representing business unit associated with application log.
    :param environment: namespace representing SDLC associated with application log.
    :return:
    """
    for abs_file_path in files_to_upload:
        log_name = abs_file_path.split('/')[-1]
        application_name = abs_file_path.split('/')[2]
        date_time = log_name.split('.')[-4]
        year, month, day = date_time.split('-')
        files_to_upload[
            abs_file_path] = f"log-archive/{business_unit}/{environment}/{application_name}/{year}/{month}/{day}/{log_name}"


def check_object_is_missing(files_to_upload: Dict[str, str], files_to_remove: Set[str], bucket: str) -> None:
    """
    Checks if remote_file_path exists in S3 Bucket. If it does, then file is removed as a candidate.
    :param files_to_remove: Set of files which are candidates for removal
    :param files_to_upload: Dictionary of files which are candidates for upload.
    :param bucket: Name of S3 Bucket where files will be uploaded to.
    :return:
    """
    for abs_file_path in list(files_to_upload.keys()):
        try:
            s3_client.head_object(Bucket=bucket, Key=files_to_upload[abs_file_path])
            del files_to_upload[abs_file_path]
            logger.info(f"{abs_file_path} exists in remote storage")
            files_to_remove.add(abs_file_path)
        except ClientError as e:
            if e.response['ResponseMetadata']['HTTPStatusCode'] != 404:
                logger.info(f"Unexpected error with {abs_file_path}, {e}")
                del files_to_upload[abs_file_path]


def summary_logging(files_to_upload: Dict[str, str], files_to_compress: Set[str], files_to_remove: Set[str]):
    """
    Provides a summary report of files uploaded, compressed and removed.
    :param files_to_upload: Dictionary of files which are candidates for upload.
    :param files_to_compress: Set of file paths which need to be compressed
    :param files_to_remove: Set of files which are candidates for removal
    :return:
    """
    logger.info(f"___________________")
    logger.info(f"Uploaded files")
    for f in files_to_upload:
        logger.info("- " + f)
        logger.info("  " + files_to_upload[f])

    logger.info(f"___________________")
    logger.info(f"Compressed files")
    for f in files_to_compress:
        logger.info("- " + f)

    logger.info(f"___________________")
    logger.info(f"Removed files")
    for f in files_to_remove:
        logger.info("- " + f)
    logger.info(f"___________________")


def handler(**kwargs):
    """
    Main function for log_archiver
    :param kwargs:
    :return:
    """
    log_expiry_age_days = int(kwargs.get('log_expiry_age'))
    business_unit = kwargs.get('business_unit')
    environment = kwargs.get('environment')
    bucket = kwargs.get('bucket')
    hostname = kwargs.get('hostname', socket.gethostname())
    dry_run = kwargs.get('dry_run', False)
    log_path = kwargs.get('log_path')

    path = glob.glob(log_path)
    now = time.time()

    files_to_compress, files_to_upload, files_to_remove = find_files(path, now, log_expiry_age_days)
    compress_file(files_to_compress, files_to_upload, hostname, dry_run)
    create_remote_path(files_to_upload, business_unit, environment)
    check_object_is_missing(files_to_upload, files_to_remove, bucket)
    if not dry_run:
        upload_s3(files_to_upload, bucket, files_to_remove, now, log_expiry_age_days)
        remove_file(files_to_remove)
    summary_logging(files_to_upload, files_to_compress, files_to_remove)
