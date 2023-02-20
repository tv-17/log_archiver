from setuptools import setup

setup(
    name="log_archiver",
    version='0.1',
    packages=["log_archiver"],
    install_requires=[
        'Click==8.1.3',
        'boto3==1.26.73'
    ],
    entry_points='''
        [console_scripts]
        log_archiver=cli:cli
    ''',
)
