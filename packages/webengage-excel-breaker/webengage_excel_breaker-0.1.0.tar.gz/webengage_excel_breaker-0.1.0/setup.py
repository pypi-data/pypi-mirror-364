from setuptools import setup, find_packages

setup(
    name="webengage-excel-breaker",
    version="0.1.0",
    packages=find_packages(),
    install_requires=['openpyxl>=3.1.2'],
    entry_points={
        "console_scripts": [
            "we=excel_breaker.excelBreaker:main",
        ],
    },
    author="Nipun Patel",
    author_email="nipunp27@gmail.com",
    description="Webengage internal tool to split Excel or CSV files multiple tabs into separate CSV files with streaming support",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://www.webengage.com/",
    license="MIT",
    license_files=["LICEN[CS]E.*"], 
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6"
)
