from setuptools import setup, find_packages

setup(
    name="airflow_slurm_executor",
    version="0.0.4",
    author="Sunset666",
    author_email="sunset666@sunset666.net",
    description="Plugin for Airflow to connect to slurm clusters",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/sunset666/Airflow-Slurm-Executor",
    packages=find_packages(),
    classifiers=["Programming Language :: Python :: 3",
                 "License :: OSI Approved :: Apache Software License",
                 "Operating System :: OS Independent"],
    python_requires=">=3.6",
    install_requires=["apache-airflow>=2.5.3"],
)
