# setup.py
import setuptools
import os

# Get the version from the environment variable set by the GitHub workflow
version = os.getenv("RELEASE_VERSION", "0.0.1")

setuptools.setup(
    name="tensorflow_serving_config",
    version=version.replace("v", ""), # Strips the 'v' from tag like v1.2.3
    author="Colorblank",
    author_email="colorblank@example.com",
    description="Python utilities for reading, writing, and validating TensorFlow Serving models.config",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/colorblank/tensorflow_serving_config",
    license="Apache-2.0", # TensorFlow and Serving use Apache 2.0
    packages=setuptools.find_packages(where='src'),
    package_dir={'': 'src'},
    # The generated files depend on these packages
    install_requires=[
        "grpcio>=1.73.1",
        "protobuf>=6.31.1",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
