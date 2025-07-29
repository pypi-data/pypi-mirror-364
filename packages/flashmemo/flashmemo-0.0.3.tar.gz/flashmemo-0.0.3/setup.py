from setuptools import setup, find_packages

setup(
    name="flashmemo",
    version="0.0.3",
    packages=find_packages(),  # important : détecte tous les modules
    include_package_data=True,
    install_requires=[],
    entry_points={
        "console_scripts": [
            "flashmemo=flashmemo.cli:main",  # pour le CLI
        ],
    },
    author="Digital Dreamer",
    author_email="digitaldreamer@gmail.com",
    description="Un outil CLI pour créer et réviser avec des cartes mémoire",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.7",
)
