from setuptools import setup, find_packages

setup(
    name='joinads',
    version='0.1.0',
    packages=find_packages(include=["joinads", "joinads.*"]),
    install_requires=[
        'python-dotenv',
        'requests',
        'fastapi',
        'dbutils',
        'pytz',
        'pymysql',
        'rich',
        'typer',
        'uvicorn'
    ],
    entry_points={
        'console_scripts': [
            'joinads=joinads.cli:main'
        ],
    },
)
