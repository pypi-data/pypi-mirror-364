from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="easypath",
    version="0.1.0",
    author="Aarav Maloo",
    author_email="aaravmaloo06@gmail.com",
    description="Cross-platform file and folder utility functions in Python made simple.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aaravmaloo/easypath", 
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Topic :: Utilities",
        "Topic :: System :: Filesystems",
    ],
    python_requires=">=3.9",
    include_package_data=True,
    zip_safe=False,
)
