from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="django-export-edit-import",
    version="1.0.1",
    author="Daniil Pevzner",
    description="Reusable Django app that enables export, edit and import (Excel) workflow.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/PevznerDanill/django-export-edit-import-package",
    packages=find_packages(include=['export_edit_import*']),
    classifiers=[
        "Framework :: Django",
        "Framework :: Django :: 4",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.9",
    install_requires=[
        "Django>=4.2",
        "pandas>=2.0",
        "openpyxl>=3.1",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-django",
            "black",
            "isort",
            "flake8",
        ],
    },
    include_package_data=True,
)
