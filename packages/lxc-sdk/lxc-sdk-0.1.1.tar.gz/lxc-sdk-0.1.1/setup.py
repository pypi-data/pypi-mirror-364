from setuptools import setup, find_packages

setup(
    name="lxc-sdk",            
    version="0.1.1",
    packages=find_packages(include=["lxc", "lxc.*"]),
    include_package_data=True,
    install_requires=["natsort", "numpy", "requests"],
    description="Tools for LXC's convenient use <3",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Asterys",
    author_email="darkbug11@foxmail.com",
    url="",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)

# pypi-AgEIcHlwaS5vcmcCJDUyN2E1ZWYwLWFmNDYtNGE5OS1iZWVmLTE2Y2E3MjZkMGM2NAACKlszLCJjOWJkM2U3MS04MzljLTQzZDctODZkOS01ZDA5YWEzMGEzMzIiXQAABiC159pSASOjz_hYoj14UYuB0A1aFF7tSXaxnwtwj7VzSg