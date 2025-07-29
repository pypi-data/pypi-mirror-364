from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="hestia-dbeaver-connector",
    version="0.1.0",
    author="Hestia Development Team",
    author_email="dev@hestia.com",
    description="DBeaver integration plugin for Hestia data platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hestia/dbeaver-connector",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "PyQt5>=5.15.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-qt>=4.0",
            "black>=21.0",
            "flake8>=3.8",
        ],
    },
    entry_points={
        "hestia.plugins": [
            "dbeaver = hestia_dbeaver_connector:register_with_hestia",
        ],
    },
    include_package_data=True,
    zip_safe=False,
) 