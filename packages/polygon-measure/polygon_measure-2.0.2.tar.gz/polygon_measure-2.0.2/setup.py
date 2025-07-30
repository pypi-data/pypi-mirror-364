"""
Setup configuration for polygon measurement tool package.
"""

from setuptools import setup, find_packages
import os


# Read metadata from package
def get_metadata():
    metadata = {}
    version_file = os.path.join("polygon_measure", "__init__.py")
    with open(version_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("__version__"):
                metadata["__version__"] = (
                    line.split("=")[1].strip().strip('"').strip("'")
                )
            elif line.startswith("__author__"):
                metadata["__author__"] = (
                    line.split("=")[1].strip().strip('"').strip("'")
                )
            elif line.startswith("__description__"):
                metadata["__description__"] = (
                    line.split("=")[1].strip().strip('"').strip("'")
                )
    return metadata


metadata = get_metadata()

# Read long description from README
long_description = ""
if os.path.exists("README.md"):
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()

setup(
    name="polygon-measure",
    version=metadata["__version__"],
    author=metadata["__author__"],
    description=metadata["__description__"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Vicellken/polygon-measure",
    packages=find_packages(),
    classifiers=[
        "Intended Audience :: Science/Research",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Image Processing",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.9",
    install_requires=[
        "opencv-python>=4.5.0",
        "numpy>=1.19.0",
        "pandas>=1.1.0",
        "scipy>=1.5.0",
    ],
    entry_points={
        "console_scripts": [
            "polygon-measure=polygon_measure.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="yolo, polygon, measurement, computer-vision, annotation, segmentation",
    project_urls={
        "Bug Reports": "https://github.com/Vicellken/polygon-measure/issues",
        "Source": "https://github.com/Vicellken/polygon-measure",
    },
)
