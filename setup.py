"""
Setup script for DevOps Transformation Platform
"""

from setuptools import setup, find_packages

with open("README_NEW.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="devops-transformation-platform",
    version="1.0.0",
    author="DevOps Transformation Team",
    description="DevOps maturity assessment and gamification platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/gamification",
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Quality Assurance",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "dtp-refresh=weekly_refresh:main",
            "dtp-dashboard=app:main",
            "dtp-setup=setup_database:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["config/*.yaml", "apps/*.yaml"],
    },
)
