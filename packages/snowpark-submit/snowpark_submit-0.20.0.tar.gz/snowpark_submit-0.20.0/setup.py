import os

from setuptools import find_namespace_packages, setup

THIS_DIR = os.path.dirname(os.path.realpath(__file__))

# read the version
VERSION = "0.20.0"


setup(
    name="snowpark-submit",
    version=VERSION,
    packages=find_namespace_packages(
        where="src",
        exclude=["snowflake.snowpark_submit.example_spark_applications*"],
    ),
    package_data={
        "snowflake.snowpark_submit": [
            "cluster_mode/spark_connect/resources/spcs_spec.template.yaml",
            "cluster_mode/spark_classic/resources/spcs_spec.template.yaml",
        ],
    },
    package_dir={"": "src"},
    entry_points={
        "console_scripts": [
            "snowpark-submit=snowflake.snowpark_submit.snowpark_submit:runner_wrapper",
        ],
    },
    python_requires=">=3.10,<3.13",
    install_requires=[
        "snowflake-snowpark-python>=1.32.0",
        "pyyaml>=6.0.2,<7.0.0",
    ],
)
