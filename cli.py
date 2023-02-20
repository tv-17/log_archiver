import click
import log_archiver


@click.command()
@click.option('--dry_run', is_flag=True, help="Run without uploading or archiving")
@click.option('--log_expiry_age', required=True, default="7", help="Specifies after how many days log should be archived.")
@click.option('--log_path', required=True, default="/opt/helloworld/hello/*/var/log/", help='log_archiver will target logs in this directory.')
@click.option('--business_unit', required=True, help='log_archiver will target logs in this directory.')
@click.option('--environment', required=True, help='log_archiver will target logs in this directory.')
@click.option('--bucket', required=True, help='Name of S3 bucket to store logs.')
@click.option('--hostname', required=True, default="localhost", help='Hostname to namespace application log')
def cli(**kwargs):
    log_archiver.handler(**kwargs)
