from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Lire le README pour la description longue
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="easyssh-cli",
    version="1.0.0",
    description="Un outil CLI élégant pour gérer et se connecter facilement à vos serveurs SSH",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/basile-parent/easyssh",
    author="Basile Parent",
    author_email="basile.parent@example.com",  # Remplacez par votre email
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    keywords="ssh, cli, terminal, server, management, connection",
    py_modules=["easyssh"],
    python_requires=">=3.7, <4",
    install_requires=[
        "rich>=13.0.0",
        "textual>=0.41.0",
        "pyfiglet>=0.8.0",
        "colorama>=0.4.0",
        "paramiko>=3.0.0",
        "click>=8.0.0",
    ],
    extras_require={
        "dev": ["pytest>=6.0", "pytest-cov", "black", "flake8"],
    },
    entry_points={
        "console_scripts": [
            "easyssh=easyssh:cli",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/basile-parent/easyssh/issues",
        "Source": "https://github.com/basile-parent/easyssh",
        "Documentation": "https://github.com/basile-parent/easyssh#readme",
    },
)