from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="linkgrid-agent",
    version="0.1.9",
    packages=find_packages(),
    install_requires=["httpx"],
    author="Deep Saha",
    author_email="hiremeasadeveloper@gmail.com",
    description="LinkGrid Agent - Python client for BitNet API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/OfficialDeepSaha/linkgrid-agent",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
)
