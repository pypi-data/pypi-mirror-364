from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="swift-iso20022-toolbox",
    version="0.1.0",
    description="Streamlit-based toolbox for uploading, parsing, and aggregating ISO 20022 payment message files (CSV, XML, Excel, XSD)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Yous Guil",
    url="https://github.com/yousdin/swift-iso20022-payment-mt2mx-toolbox", 
    license="MIT", 
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    install_requires=[
        "streamlit",
        "pandas",
        "openpyxl",
        "xlsxwriter",
    ],
    entry_points={
        "console_scripts": [
            "iso20022-toolbox=swift_iso20022_toolbox.iso20022_toolbox:main",
        ]
    },
    include_package_data=True,
    python_requires=">=3.7",
)
