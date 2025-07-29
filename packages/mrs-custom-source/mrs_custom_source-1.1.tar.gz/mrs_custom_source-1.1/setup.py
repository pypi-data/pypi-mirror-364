from setuptools import find_packages, setup

setup_output = setup(
    name="mrs_custom_source",
    version="1.1",
    description="MRS for Datahub custom sources",
    package_dir={"": "src"},
    packages=find_packages("src"),
    install_requires=["acryl-datahub"],
)
#LD_RUN_PATH=/usr/local/lib ./configure LDFLAGS="-L/usr/local/lib" CPPFLAGS="-I/usr/local/include"   --prefix=/usr/local/python3
