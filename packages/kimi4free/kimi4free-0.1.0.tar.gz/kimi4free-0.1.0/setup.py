from setuptools import setup, find_packages
import pathlib

current_dir = pathlib.Path(__file__).parent
long_description = (current_dir / "README.md").read_text(encoding="utf-8")

setup(
    name="kimi4free",
    version="0.1.0",
    author="SertraFurr",
    description="A way of using Kimi for free; even with login features.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SertraFurr/kimi4free", 
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=[
        "requests",
    ],
    include_package_data=True,
)