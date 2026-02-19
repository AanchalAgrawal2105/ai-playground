"""Setup configuration for the airflow-monitoring package."""

from setuptools import setup, find_packages

# Read README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="airflow-monitoring",
    version="1.0.0",
    author="HelloFresh Data Team",
    author_email="aanchal.agrawal@hellofresh.com",
    description="Airflow Runtime Monitoring with Slack Integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hellofresh/airflow-monitoring",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: System :: Monitoring",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-asyncio>=0.20.0",
            "pytest-cov>=4.0",
            "black>=22.0",
            "isort>=5.0",
            "flake8>=5.0",
            "mypy>=1.0",
            "pre-commit>=2.20.0",
        ],
        "test": [
            "pytest>=7.0",
            "pytest-asyncio>=0.20.0",
            "pytest-cov>=4.0",
            "responses>=0.22.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "airflow-monitor=airflow_monitoring.airflow_runtime_agent:main",
            "airflow-mcp-server=airflow_monitoring.airflow_mcp_server:main",
            "slack-mcp-server=airflow_monitoring.slack_mcp_server:main",
        ],
    },
    package_data={
        "airflow_monitoring": ["*.yaml", "*.yml", "*.json"],
    },
    include_package_data=True,
)