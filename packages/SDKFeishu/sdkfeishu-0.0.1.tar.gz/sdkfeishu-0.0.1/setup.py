from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="SDKFeishu",
    version="0.0.1",
    author="SRInternet",
    author_email="srinternet@qq.com",
    description="Third-party Python SDK for Feishu Open Platform API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SRInternet/SDKFeishu",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.1",
        "requests-toolbelt>=0.9.1"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
