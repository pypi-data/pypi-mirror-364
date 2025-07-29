"""
Setup configuration for mailopt CLI tool.
"""

from setuptools import setup, find_packages

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mailopt",
    version="0.1.0",
    author="Souleymane SALL",
    author_email="souleymanesallvml@gmail.com",
    description="CLI Python pour automatiser et optimiser les workflows email/front-end",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vml-marketing-mail/mailopt",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Communications :: Email",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    install_requires=[
        "click>=8.0.0",
        "beautifulsoup4>=4.9.0",
        "lxml>=4.6.0",  # Better HTML parser for BeautifulSoup
        "importlib_metadata>=4.0.0;python_version<'3.8'",  # For older Python versions
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "flake8>=5.0.0",
            "pylint>=2.15.0",
            "black>=22.0.0",
            "mypy>=1.0.0",
            "bandit>=1.7.0",
            "safety>=2.0.0",
        ],
        "test": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "mailopt=mailopt.cli:main",
        ],
        "mailopt.commands": [
            "check-images=mailopt.commands.images:check_images",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="email, cli, automation, optimization, frontend, workflow",
    project_urls={
        "Bug Reports": "https://github.com/vml-marketing-mail/mailopt/issues",
        "Source": "https://github.com/vml-marketing-mail/mailopt",
        "Documentation": "https://github.com/vml-marketing-mail/mailopt#readme",
    },
)
