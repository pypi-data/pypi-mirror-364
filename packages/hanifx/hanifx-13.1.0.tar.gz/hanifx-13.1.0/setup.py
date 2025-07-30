# setup.py

from setuptools import setup, find_packages

setup(
    name="hanifx",
    version="13.1.0",
    author="Hanif",
    description="Twine alternative: PyPI uploader with auto-build",
    packages=find_packages(),
    install_requires=["requests"],
    entry_points={
        "console_scripts": [
            "hanifx-upload=hanifx.cli:main",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.6',
)
