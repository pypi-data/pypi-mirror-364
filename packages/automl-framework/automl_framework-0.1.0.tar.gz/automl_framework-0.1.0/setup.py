"""
Setup script for AutoML Framework
"""

from setuptools import setup, find_packages
import os


def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()


def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [
            line.strip() for line in fh if line.strip() and not line.startswith("#")
        ]


def read_version():
    version_file = os.path.join("automl", "__version__.py")
    if os.path.exists(version_file):
        with open(version_file, "r") as f:
            exec(f.read())
            return locals()["__version__"]
    return "0.1.0"


setup(
    name="automl-framework",
    version=read_version(),
    author="Nanda Rizkika Ruanawijaya",
    author_email="nandarizky52@gmail.com",
    description="A comprehensive, modular framework for automated machine learning with overfitting detection and mitigation",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/nandarizkika/automl-framework",
    project_urls={
        "Bug Tracker": "https://github.com/nandarizkika/automl-framework/issues",
        "Documentation": "https://github.com/nandarizkika/automl-framework/docs",
        "Source Code": "https://github.com/nandarizkika/automl-framework",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.12.0",
            "black>=21.0.0",
            "flake8>=3.9.0",
            "isort>=5.9.0",
        ],
        "docs": [
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=0.5.0",
        ],
        "jupyter": [
            "jupyter>=1.0.0",
            "ipykernel>=6.0.0",
            "notebook>=6.4.0",
        ],
        "advanced": [
            "scikit-optimize>=0.9.0",
            "hyperopt>=0.2.7",
        ],
        "all": [
            "pytest>=6.0.0",
            "pytest-cov>=2.12.0",
            "black>=21.0.0",
            "flake8>=3.9.0",
            "isort>=5.9.0",
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=0.5.0",
            "jupyter>=1.0.0",
            "ipykernel>=6.0.0",
            "notebook>=6.4.0",
            "scikit-optimize>=0.9.0",
            "hyperopt>=0.2.7",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords=[
        "machine learning",
        "automl",
        "automated machine learning",
        "overfitting",
        "hyperparameter tuning",
        "model selection",
        "scikit-learn",
    ],
)
