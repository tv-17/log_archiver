# log_archiver

## What is it?
log_archiver is a rotation, backup and archival tool written in Python. 
This was designed to replace several features offered by the OS package log_rotate.

## Installation

```
$ git clone https://github.com/tv-17/log_archiver
$ sudo apt install python3.10-venv
$ python3 -m venv env
$ source env/bin/activate
$ cd log_archiver
$ python3 -m pip install .
```

## Help

```
$ log_archiver --help

Usage: log_archiver [OPTIONS]

Options:
  --dry_run              Run without uploading or archiving
  --log_expiry_age TEXT  Specifies after how many days log should be archived.
                         [required]
  --log_path TEXT        log_archiver will target logs in this directory.
                         [required]
  --business_unit TEXT   log_archiver will target logs in this directory.
                         [required]
  --environment TEXT     log_archiver will target logs in this directory.
                         [required]
  --bucket TEXT          Name of S3 bucket to store logs.  [required]
  --hostname TEXT        Hostname to namespace application log  [required]
  --help                 Show this message and exit.
```

## Usage 

1. Create log file `/opt/helloworld/hello/var/log/hello.2023-02-16.log`

```
$ log_archiver --business_unit test --environment dev --bucket company-regulatory-archive
[2023-02-20 14:38:45,672] [INFO] [MainThread] - Finding uncompressed files in ['/opt/helloworld/hello/var/log/']
[2023-02-20 14:38:45,672] [INFO] [MainThread] - Adding /opt/helloworld/hello/var/log/hello.2023-02-20.log to compression queue.
[2023-02-20 14:38:46,151] [INFO] [MainThread] - Uploaded /opt/helloworld/hello/var/log/hello.2023-02-20.log.localhost.gz to remote storage
[2023-02-20 14:38:46,152] [INFO] [MainThread] - hello.2023-02-20.log.localhost.gz
[2023-02-20 14:38:46,152] [INFO] [MainThread] - /opt/helloworld/hello/var/log/hello.2023-02-20.log.localhost.gz 1676851200
[2023-02-20 14:38:46,152] [INFO] [MainThread] - Removed /opt/helloworld/hello/var/log/hello.2023-02-20.log
[2023-02-20 14:38:46,152] [INFO] [MainThread] - ___________________
[2023-02-20 14:38:46,152] [INFO] [MainThread] - Uploaded files
[2023-02-20 14:38:46,152] [INFO] [MainThread] - - /opt/helloworld/hello/var/log/hello.2023-02-20.log.localhost.gz
[2023-02-20 14:38:46,152] [INFO] [MainThread] -   log-archive/test/dev/hello/2023/02/20/hello.2023-02-20.log.localhost.gz
[2023-02-20 14:38:46,152] [INFO] [MainThread] - ___________________
[2023-02-20 14:38:46,152] [INFO] [MainThread] - Compressed files
[2023-02-20 14:38:46,152] [INFO] [MainThread] - - /opt/helloworld/hello/var/log/hello.2023-02-20.log
[2023-02-20 14:38:46,152] [INFO] [MainThread] - ___________________
[2023-02-20 14:38:46,152] [INFO] [MainThread] - Removed files
[2023-02-20 14:38:46,152] [INFO] [MainThread] - - /opt/helloworld/hello/var/log/hello.2023-02-20.log
[2023-02-20 14:38:46,152] [INFO] [MainThread] - ___________________

```

or to dry run:
```
$ log_archiver --business_unit test --environment dev --bucket company-regulatory-archive --dry_run
```


## Function Signatures

* [log_archiver](docs/modules.md)

    * [log_archiver module](docs/log_archiver.md)

## Limitations
Log paths should be namespaced like this
`/opt/<company>/<app_name>/var/log/<app_name>.<YYYY>-<MM>-<DD>.log`

