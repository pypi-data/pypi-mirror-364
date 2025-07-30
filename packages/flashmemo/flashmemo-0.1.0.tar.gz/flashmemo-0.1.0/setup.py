from setuptools import setup, find_packages
from pathlib import Path

README = (Path(__file__).parent / "README.md").read_text()

setup(
    name="flashmemo",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Flask>=2.0"  # Flask est nécessaire pour l'interface web
    ],
    entry_points={
        "console_scripts": [
            "flashmemo=flashmemo.cli:main",
        ],
    },
    author="Digital Dreamer",
    author_email="digitaldreamer@gmail.com",
    description="Un outil CLI pour créer et réviser avec des cartes mémoire",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/ton-compte/flashmemo",  # à modifier si tu as un repo
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
