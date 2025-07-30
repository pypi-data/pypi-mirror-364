from setuptools import setup, find_packages

setup(
    name="betterterminalcli",
    version="0.1.0",
    author="Maurício Reisdoefer Pereira",
    author_email="mauricio.reisdoefer2009@gmail.com",
    description="Uma biblioteca para facilitar interfaces no terminal com menus, formulários, tabelas, logs coloridos e mais.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/MauricioReisdoefer/betterterminal",
    packages=find_packages(), 
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License", 
    ],
    install_requires=[
        "readchar>=3.0.0",
    ],
    entry_points={

    },
)
