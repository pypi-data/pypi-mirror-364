from setuptools import setup, find_packages

setup(
    name="lcrpm",
    version="0.1.1",
    description="Lung Cancer Risk Profiling Module for OMOP CDM with time-to-event modeling",
    author="Yusuf Brima",
    author_email="your.email@example.com",
    packages=find_packages(include=["lcrpm", "lcrpm.*"]),
    python_requires=">=3.7",
    install_requires=[
        "python-dotenv",
        "sqlalchemy",
        "psycopg2-binary",
        "pandas",
        "matplotlib",
        "seaborn",
        "lifelines",
        "scikit-survival"
    ],
    include_package_data=True,
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)