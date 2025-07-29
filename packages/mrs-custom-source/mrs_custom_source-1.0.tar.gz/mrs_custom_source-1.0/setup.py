from setuptools import find_packages, setup

setup_output = setup(
    name="mrs_custom_source",
    version="1.0",
    description="MRS for Datahub custom sources",
    package_dir={"": "src"},
    packages=find_packages("src"),
    install_requires=["acryl-datahub"],
)