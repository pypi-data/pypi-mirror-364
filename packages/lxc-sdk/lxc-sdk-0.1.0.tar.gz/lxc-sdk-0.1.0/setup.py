from setuptools import setup, find_packages

setup(
    name="lxc-sdk",            
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["natsort", "numpy", "requests"],
    description="Tools for convenient use",
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

# pypi-AgEIcHlwaS5vcmcCJGQyMTg1ODdhLWYwNDEtNDA3MS1hYmEzLTU2YTIzYmQyMmM5NwACKlszLCJjOWJkM2U3MS04MzljLTQzZDctODZkOS01ZDA5YWEzMGEzMzIiXQAABiC8Q_bsGyGXnJvI7BlmRUByZKzzpL2Qb7Zwb0DF0nzJ2A