from setuptools import setup, find_packages

setup(
    name="echo-report-lab",
    version="0.1.2",
    author="Patrick Rutledge",
    description="Civic-grade CNN training lab with HTML export and symbolic reporting",
    packages=find_packages(exclude=["tests", "*.ipynb"]),
    include_package_data=True,
    install_requires=[
        "tensorflow-cpu",
        "keras",
        "matplotlib",
        "scikit-learn",
        "numpy",
        "pandas"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.12",
)
