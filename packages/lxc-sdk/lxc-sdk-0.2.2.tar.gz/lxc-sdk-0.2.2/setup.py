from setuptools import setup, find_packages

setup(
    name="lxc-sdk",            
    version="0.2.2",
    packages=find_packages(include=["lxc", "lxc.*"]),
    include_package_data=True,
    install_requires=["natsort", "numpy", "requests",
                      "keyboard", "mooredata-sdk", "tqdm", "laspy"],
    description="Tools for convenient developing <3",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Starlight",
    author_email="darkbug11@foxmail.com",
    url="",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)