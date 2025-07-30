from setuptools import setup, find_packages

setup(
    name="redactify-ai",
    version="0.0.1",
    description="A Python package for leveraging Presidio for anonymizing sensitive PII data using Spark.",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author="Roman Korolev",
    author_email="spark_development@yahoo.com",
    url="https://gitlab.com/rokorolev/redactify-ai",
    license='MIT',
    packages=find_packages(include=["redactify_ai"],exclude=["tests", "examples"]),
    include_package_data=True,
    install_requires=[
        "pyyaml==6.0.1",
        "pandas==1.5.3",
        "spacy==3.7.5",
        "presidio_analyzer~=2.2.358",
        "presidio_anonymizer~=2.2.358",
        "requests==2.32.2",
        "urllib3==1.26.16",
        "pyspark==3.5.2"
    ],
    python_requires=">=3.11",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
)
