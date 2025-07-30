"""Setup script for qt-lottie package"""

from setuptools import setup, find_packages
import os

# Read the long description from README
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

# Read version from __init__.py
def get_version():
    version_file = os.path.join('qtlottie', '__init__.py')
    with open(version_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip('"\'')
    return "0.1.0"

setup(
    name="qt-lottie",
    version=get_version(),
    author="Qt Lottie Contributors",
    author_email="",
    description="Cross-platform Python library providing Lottie animation support for Qt applications",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/qt-lottie",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Software Development :: User Interfaces",
    ],
    python_requires=">=3.8",
    install_requires=[
        "rlottie-python>=1.0.0",
    ],
    extras_require={
        "pyside6": ["PySide6>=6.0.0"],
        "pyqt6": ["PyQt6>=6.0.0"],
        "dev": [
            "pytest>=6.0",
            "pytest-qt>=4.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.900",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
        ],
    },
    package_data={
        "qtlottie": ["py.typed"],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="qt lottie animation qml pyside6 pyqt6 graphics",
    project_urls={
        "Bug Reports": "https://github.com/your-org/qt-lottie/issues",
        "Source": "https://github.com/your-org/qt-lottie",
        "Documentation": "https://qt-lottie.readthedocs.io/",
    },
)